import smtplib

EMAIL_HOST = "smtp.zoho.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "malakaya.lauvergnat@malakayalauvergnat.com"  # Remplacez par votre adresse Zoho complète
EMAIL_HOST_PASSWORD = "jWJchVFsZtQp"      # Mot de passe ou mot de passe d'application

try:
    server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
    server.set_debuglevel(1)  # Active le mode debug pour voir les détails
    server.starttls()
    server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
    print("Connexion réussie.")
    server.quit()
except Exception as e:
    print(f"Erreur : {e}")
