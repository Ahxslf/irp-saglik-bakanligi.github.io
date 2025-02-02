from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, SelectField, FileField, TextAreaField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileRequired
from flask_wtf.recaptcha import RecaptchaField
from datetime import timedelta
import os
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['RECAPTCHA_PUBLIC_KEY'] = os.getenv('RECAPTCHA_PUBLIC_KEY')
app.config['RECAPTCHA_PRIVATE_KEY'] = os.getenv('RECAPTCHA_PRIVATE_KEY')
app.permanent_session_lifetime = timedelta(minutes=30)
app.config['UPLOAD_FOLDER'] = 'uploads/'

class LoginForm(FlaskForm):
    password = PasswordField('Giriş Şifresi', validators=[DataRequired()])
    submit = SubmitField('Giriş')

class AdminForm(FlaskForm):
    key = StringField('Anahtar', validators=[DataRequired()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    submit = SubmitField('Giriş')

class CaptchaForm(FlaskForm):
    recaptcha = RecaptchaField()
    submit = SubmitField('Doğrula')

class HastaKayitForm(FlaskForm):
    kayit_no = StringField('Kayıt No', validators=[DataRequired()])
    tc_no = StringField('T.C. Kimlik No', validators=[DataRequired()])
    adi = StringField('Adı', validators=[DataRequired()])
    soyadi = StringField('Soyadı', validators=[DataRequired()])
    cinsiyeti = SelectField('Cinsiyeti', choices=[('Kadın', 'Kadın'), ('Erkek', 'Erkek')], validators=[DataRequired()])
    uyrugu = SelectField('Uyruğu', choices=[('T.C.', 'T.C.'), ('Diğer', 'Diğer')], validators=[DataRequired()])
    dogum_tarihi = StringField('Doğum Tarihi', validators=[DataRequired()])
    dogum_yeri = StringField('Doğum Yeri', validators=[DataRequired()])
    vesikalik = FileField('Vesikalık', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Sadece resim dosyaları!')])
    aktif_hastaliklar = TextAreaField('Aktif Hastalıklar', validators=[DataRequired()])
    test_no = StringField('Yapıldıysa Test No')
    hastaneye_gelis_sebebi = TextAreaField('Hastaneye Geliş Sebebi', validators=[DataRequired()])
    mudahaleler = TextAreaField('Müdahaleler', validators=[DataRequired()])
    mudahale_edenler = TextAreaField('Müdahale Edenler', validators=[DataRequired()])
    triyaj = SelectField('Triyaj', choices=[('Yeşil', 'Yeşil'), ('Sarı', 'Sarı'), ('Kırmızı', 'Kırmızı'), ('Siyah', 'Siyah')], validators=[DataRequired()])
    imza_kase = FileField('Dosyayı Tutan İmza - Kaşe', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Sadece resim dosyaları!')])
    submit = SubmitField('Gönder')

def save_form_to_image(form_data):
    # Boş şablon fotoğrafını yükle
    image = Image.open('static/images/sablon.png')
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    # Form verilerini şablona yerleştir
    draw.text((50, 50), f"Kayıt No: {form_data['kayit_no']}", font=font, fill='black')
    draw.text((50, 100), f"T.C. Kimlik No: {form_data['tc_no']}", font=font, fill='black')
    draw.text((50, 150), f"Adı: {form_data['adi']}", font=font, fill='black')
    draw.text((50, 200), f"Soyadı: {form_data['soyadi']}", font=font, fill='black')
    draw.text((50, 250), f"Cinsiyeti: {form_data['cinsiyeti']}", font=font, fill='black')
    draw.text((50, 300), f"Uyruğu: {form_data['uyrugu']}", font=font, fill='black')
    draw.text((50, 350), f"Doğum Tarihi: {form_data['dogum_tarihi']}", font=font, fill='black')
    draw.text((50, 400), f"Doğum Yeri: {form_data['dogum_yeri']}", font=font, fill='black')
    draw.text((50, 450), f"Aktif Hastalıklar: {form_data['aktif_hastaliklar']}", font=font, fill='black')
    draw.text((50, 500), f"Test No: {form_data['test_no']}", font=font, fill='black')
    draw.text((50, 550), f"Hastaneye Geliş Sebebi: {form_data['hastaneye_gelis_sebebi']}", font=font, fill='black')
    draw.text((50, 600), f"Müdahaleler: {form_data['mudahaleler']}", font=font, fill='black')
    draw.text((50, 650), f"Müdahale Edenler: {form_data['mudahale_edenler']}", font=font, fill='black')
    draw.text((50, 700), f"Triyaj: {form_data['triyaj']}", font=font, fill='black')

    # Resmi kaydet
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'hasta_kayit_dosyasi.png')
    image.save(output_path)
    return output_path

@app.route('/', methods=['GET', 'POST'])
def index():
    login_form = LoginForm()
    admin_form = AdminForm()
    captcha_form = CaptchaForm()

    if request.method == 'POST':
        if login_form.validate_on_submit():
            if 'login_attempts' not in session:
                session['login_attempts'] = 0
            if login_form.password.data == os.getenv('LOGIN_PASSWORD'):
                session.permanent = True
                session['user'] = 'personel'
                session['login_attempts'] = 0
                return redirect(url_for('personel_portal'))
            else:
                session['login_attempts'] += 1
                flash('Yanlış şifre. Lütfen tekrar deneyiniz.', 'danger')
                if session['login_attempts'] >= 5:
                    return render_template('captcha.html', form=captcha_form)
        
        if admin_form.validate_on_submit():
            if 'admin_attempts' not in session:
                session['admin_attempts'] = 0
            if admin_form.key.data == os.getenv('ADMIN_KEY') and admin_form.password.data == os.getenv('ADMIN_PASSWORD'):
                session.permanent = True
                session['user'] = 'admin'
                session['admin_attempts'] = 0
                return redirect(url_for('admin_portal'))
            else:
                session['admin_attempts'] += 1
                flash('Yanlış anahtar veya şifre. Lütfen tekrar deneyiniz.', 'danger')
                if session['admin_attempts'] >= 5:
                    return render_template('captcha.html', form=captcha_form)

    return render_template('index.html', login_form=login_form, admin_form=admin_form)

@app.route('/captcha', methods=['GET', 'POST'])
def captcha():
    captcha_form = CaptchaForm()
    if request.method == 'POST':
        if captcha_form.validate_on_submit():
            flash('Captcha doğrulandı. Lütfen tekrar giriş yapın.', 'success')
            session['login_attempts'] = 0
            session['admin_attempts'] = 0
            return redirect(url_for('index'))
        flash('Captcha doğrulanamadı. Lütfen tekrar deneyin.', 'danger')
    return render_template('captcha.html', form=captcha_form)

@app.route('/personel_portal')
def personel_portal():
    if 'user' in session and session['user'] == 'personel':
        return render_template('personel_portal.html')
    return redirect(url_for('index'))

@app.route('/admin_portal')
def admin_portal():
    if 'user' in session and session['user'] == 'admin':
        return render_template('admin_portal.html')
    return redirect(url_for('index'))

@app.route('/hasta_kayit_dosyasi', methods=['GET', 'POST'])
def hasta_kayit_dosyasi():
    form = HastaKayitForm()
    if form.validate_on_submit():
        form_data = {
            'kayit_no': form.kayit_no.data,
            'tc_no': form.tc_no.data,
            'adi': form.adi.data,
            'soyadi': form.soyadi.data,
            'cinsiyeti': form.cinsiyeti.data,
            'uyrugu': form.uyrugu.data,
            'dogum_tarihi': form.dogum_tarihi.data,
            'dogum_yeri': form.dogum_yeri.data,
            'aktif_hastaliklar': form.aktif_hastaliklar.data,
            'test_no': form.test_no.data,
            'hastaneye_gelis_sebebi': form.hastaneye_gelis_sebebi.data,
            'mudahaleler': form.mudahaleler.data,
            'mudahale_edenler': form.mudahale_edenler.data,
            'triyaj': form.triyaj.data,
        }
        image_path = save_form_to_image(form_data)
        flash(f'Hasta Kayıt Dosyası başarıyla oluşturuldu! Dosya yolu: {image_path}', 'success')
        return redirect(url_for('personel_portal') if session['user'] == 'personel' else url_for('admin_portal'))
    return render_template('hasta_kayit_dosyasi.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'user' in session:
        user_type = session['user']
        return render_template('profile.html', user_type=user_type)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
