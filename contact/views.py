from django.shortcuts import render, redirect
from django.contrib import messages
from .models import NewsLetter
from .forms import ContactForm
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        
        if form.is_valid():
            contact = form.save()
            
            # Ambil data dari form
            sender_email = contact.email
            receiver_email = "ikhsansudiramubaroq2910@gmail.com"  # 🟢 Ganti dengan email kamu sendiri
            
            # Format email
            subject = f"[Contact Form] {contact.subject}"
            text_message = f"""
            Nama  : {contact.name}
            Email : {contact.email}

            Pesan:
            {contact.message}
            """
            html_message = f"""
            <div style="font-family: Arial, sans-serif; padding: 10px; color: #333;">
                <h2 style="color:#2c3e50;">📬 New Contact Message</h2>
                <p><strong>Name:</strong> {contact.name}</p>
                <p><strong>Email:</strong> {contact.email}</p>
                <p><strong>Subject:</strong> {contact.subject}</p>
                <hr style="border: 1px solid #eee;">
                <p style="white-space: pre-wrap;">{contact.message}</p>
            </div>
            """

            # Kirim email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_message,
                from_email=f"{contact.name} <{sender_email}>",  # 🟢 jadi pengirim adalah user asli
                to=[receiver_email],  # 🟢 penerima kamu
                reply_to=[sender_email],  # agar tombol "Reply" di email masuk ke user
            )
            email.attach_alternative(html_message, "text/html")
            email.send()

            messages.success(request, 'Pesan kamu sudah dikirim! 🎉')
            return redirect('contact:contact')
    else:
        form = ContactForm()

    context = {
        'title' : "Contact Form",
        'form' : form
    }
    return render (request, 'contact/contact.html',context)

def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, "Please enter a valid email address.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # Cek apakah email sudah terdaftar
        if NewsLetter.objects.filter(email=email).exists():
            messages.info(request, "You're already subscribed to our newsletter.")
        else:
            NewsLetter.objects.create(email=email)
            messages.success(request, "Thank you for subscribing to our newsletter!")
        
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # fallback untuk GET request
    return redirect('/')
