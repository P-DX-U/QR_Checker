import hashlib

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .csv_import import CsvImportError, parse_csv
from .models import Post
from .views import BULK_SESSION_KEY

HEADER = 'name,last_name,email,event_type,role,event_name,theme,date,event_addr\n'
ROW_OK = 'Pancho,Villa Arango,pancho@example.com,Congreso,Escucha,Revolución Mexicana,Decena Trágica,1910-11-20,CDMX\n'
ROW_OK_2 = 'Emiliano,Zapata,emiliano@example.com,seminario,PONENTE,Revolución Mexicana,Tierra y Libertad,20/11/1910,Morelos\n'
ROW_MISSING = 'Francisco,,madero@example.com,Congreso,,Revolución Mexicana,Plan de San Luis,1910-11-20,\n'


def csv_file(content, name='asistentes.csv', encoding='utf-8'):
    return SimpleUploadedFile(name, content.encode(encoding), content_type='text/csv')


def expected_hash(name, last_name, date, event_name):
    # Same value p_utils.make_hash produces (sha256sum output + trailing newline)
    return hashlib.sha256(f'{name}{last_name}{date}{event_name}'.encode()).hexdigest() + '\n'


class ParseCsvTests(TestCase):
    def test_spanish_headers_semicolon_and_normalization(self):
        content = ('Nombre;Apellidos;Correo electrónico;Tipo de evento;Rol;Nombre del evento;Tema;Fecha;Dirección del evento;Extra\n'
                   'Ana;López;ana@example.com;congreso;escucha;Evento;Tema;05/11/2026;CDMX;x\n')
        parsed = parse_csv(csv_file(content), {
            'event_type': (('Congreso', 'Congreso'),), 'role': (('Escucha', 'Escucha'),)})
        data = parsed['rows'][0]['data']
        self.assertEqual(data['date'], '2026-11-05')
        self.assertEqual(data['event_type'], 'Congreso')
        self.assertEqual(data['role'], 'Escucha')
        self.assertEqual(parsed['missing_columns'], [])
        self.assertEqual(parsed['ignored_columns'], ['Extra'])

    def test_bom_cp1252_and_blank_lines(self):
        parsed = parse_csv(csv_file('\ufeff' + HEADER + ROW_OK + '\n,,,,\n'))
        self.assertEqual(len(parsed['rows']), 1)
        parsed = parse_csv(csv_file(HEADER + ROW_OK, encoding='cp1252'))
        self.assertEqual(parsed['rows'][0]['data']['event_name'], 'Revolución Mexicana')

    def test_missing_columns_are_reported(self):
        parsed = parse_csv(csv_file('name,last_name\nAna,López\n'))
        self.assertIn('email', parsed['missing_columns'])
        self.assertEqual(parsed['rows'][0]['data']['email'], '')

    def test_unusable_files(self):
        for content in ('', 'foo,bar\n1,2\n', HEADER):
            with self.assertRaises(CsvImportError):
                parse_csv(csv_file(content))


class BulkRegisterTests(TestCase):
    def upload(self, content):
        return self.client.post(reverse('post_bulk_upload'), {'csv_file': csv_file(content)})

    def test_main_page_has_bulk_button(self):
        self.assertContains(self.client.get('/register/'), reverse('post_bulk_upload'))
        self.assertEqual(self.client.get(reverse('post_bulk_upload')).status_code, 200)

    def test_all_valid_rows_are_registered_with_hash(self):
        response = self.upload(HEADER + ROW_OK + ROW_OK_2)
        self.assertRedirects(response, reverse('post_bulk_review'))
        review = self.client.get(reverse('post_bulk_review'))
        self.assertContains(review, 'Registrar 2 asistentes')
        self.assertEqual(Post.objects.count(), 0)  # nothing saved before confirming

        response = self.client.post(reverse('post_bulk_review'), {'action': 'confirm', 'shown': '0,1'})
        self.assertRedirects(response, reverse('post_bulk_upload'))
        self.assertEqual(Post.objects.count(), 2)
        zapata = Post.objects.get(last_name='Zapata')
        self.assertEqual(zapata.event_type, 'Seminario')
        self.assertEqual(zapata.role, 'Ponente')
        self.assertEqual(str(zapata.date), '1910-11-20')
        self.assertEqual(zapata.qr_hash, expected_hash('Emiliano', 'Zapata', '1910-11-20', 'Revolución Mexicana'))
        self.assertNotIn(BULK_SESSION_KEY, self.client.session)

    def test_missing_data_blocks_confirmation_until_completed(self):
        self.upload(HEADER + ROW_OK + ROW_MISSING)
        review = self.client.get(reverse('post_bulk_review'))
        self.assertContains(review, 'Línea 3 del CSV')
        self.assertContains(review, 'name="row-1-last_name"')
        self.assertContains(review, 'disabled')

        # Confirming with invalid rows saves nothing
        self.client.post(reverse('post_bulk_review'), {'action': 'confirm', 'shown': '1,0'})
        self.assertEqual(Post.objects.count(), 0)

        # The operator completes the missing fields
        fix = {f'row-1-{k}': v for k, v in {
            'name': 'Francisco', 'last_name': 'Madero', 'email': 'madero@example.com',
            'event_type': 'Congreso', 'role': 'Ponente', 'event_name': 'Revolución Mexicana',
            'theme': 'Plan de San Luis', 'date': '1910-11-20', 'event_addr': 'San Luis Potosí'}.items()}
        self.client.post(reverse('post_bulk_review'), {**fix, 'action': 'revalidate', 'shown': '1,0'})
        review = self.client.get(reverse('post_bulk_review'))
        self.assertContains(review, 'Registrar 2 asistentes')

        self.client.post(reverse('post_bulk_review'), {'action': 'confirm', 'shown': '0,1'})
        self.assertEqual(Post.objects.count(), 2)
        madero = Post.objects.get(last_name='Madero')
        self.assertEqual(madero.event_addr, 'San Luis Potosí')
        self.assertEqual(madero.qr_hash, expected_hash('Francisco', 'Madero', '1910-11-20', 'Revolución Mexicana'))

    def test_blank_values_stay_invalid(self):
        self.upload(HEADER + ROW_MISSING)
        blank = {f'row-0-{k}': '  ' for k in ('name', 'last_name', 'email', 'event_type', 'role',
                                               'event_name', 'theme', 'date', 'event_addr')}
        self.client.post(reverse('post_bulk_review'), {**blank, 'action': 'confirm', 'shown': '0'})
        self.assertEqual(Post.objects.count(), 0)
        self.assertContains(self.client.get(reverse('post_bulk_review')), 'Registros por completar')

    def test_discarded_rows_are_not_saved(self):
        self.upload(HEADER + ROW_OK + ROW_MISSING)
        self.client.post(reverse('post_bulk_review'), {'row-1-discard': 'on', 'action': 'confirm', 'shown': '1,0'})
        self.assertEqual(list(Post.objects.values_list('name', flat=True)), ['Pancho'])

    def test_duplicates_are_skipped(self):
        Post.objects.create(name='Pancho', last_name='Villa Arango', email='p@example.com',
                            event_type='Congreso', role='Escucha', event_name='Revolución Mexicana',
                            theme='x', date='1910-11-20', event_addr='x',
                            qr_hash=expected_hash('Pancho', 'Villa Arango', '1910-11-20', 'Revolución Mexicana'))
        self.upload(HEADER + ROW_OK + ROW_OK_2 + ROW_OK_2)
        review = self.client.get(reverse('post_bulk_review'))
        self.assertContains(review, 'Ya registrado')
        self.assertContains(review, 'Duplicado de línea 3')
        self.client.post(reverse('post_bulk_review'), {'action': 'confirm', 'shown': '0,1,2'})
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(Post.objects.filter(last_name='Zapata').count(), 1)

    def test_invalid_upload_shows_error(self):
        self.assertContains(self.upload('foo,bar\n1,2\n'), 'No se reconoció ninguna columna')
        response = self.client.post(reverse('post_bulk_upload'),
                                    {'csv_file': SimpleUploadedFile('a.txt', b'x')})
        self.assertContains(response, 'extensión .csv')

    def test_review_without_upload_redirects(self):
        self.assertRedirects(self.client.get(reverse('post_bulk_review')), reverse('post_bulk_upload'))

    def test_cancel_clears_session(self):
        self.upload(HEADER + ROW_OK)
        self.client.post(reverse('post_bulk_cancel'))
        self.assertNotIn(BULK_SESSION_KEY, self.client.session)

    def test_template_download(self):
        response = self.client.get(reverse('post_bulk_template'))
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('name,last_name,email', response.content.decode('utf-8-sig'))
