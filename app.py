from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, SelectField, FileField, TextAreaField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileRequired
from flask_wtf.recaptcha import RecaptchaField
from datetime import timedelta

app = Flask(__name__)
app.secret_key = '6Lc_fcoqAAAAAD6hz9mOMvrfljZPSaLKKMnPeMRm'  # Update with a secure secret key
app.config['RECAPTCHA_PUBLIC_KEY'] = '6Lc_fcoqAAAAAEcZvCLaHLm-RqBpKXNB6uqM6IRC'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Lc_fcoqAAAAAD6hz9mOMvrfljZPSaLKKMnPeMRm'
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

@app.route('/', methods=['GET', 'POST'])
def index():
    login_form = LoginForm()
    admin_form = AdminForm()
    captcha_form = CaptchaForm()

    if request.method == 'POST':
        if login_form.validate_on_submit():
            if 'login_attempts' not in session:
                session['login_attempts'] = 0
            if login_form.password.data == '495012':
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
            if admin_form.key.data == '3ed8eecf16a7ca9ecde6d20602dfafa27a4268077201d221537441b446b66183' and admin_form.password.data == 'i-@l}[JF.Pv-C%tdZJ29.0-[qCNe2YfWg}QT]b_XBpVq!ibqwm':
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
        # Dosya işlemleri burada yürütülecek
        flash('Hasta Kayıt Dosyası başarıyla oluşturuldu!', 'success')
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
