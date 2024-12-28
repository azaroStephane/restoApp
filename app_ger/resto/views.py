from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import RegistrationForm, ReservationForm
from django.contrib import messages
from django.utils import timezone
from .models import Reservation, Dish, Panier, ItemPanier
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
import requests
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

def confirmation(request):
    template_c = loader.get_template('resto/confirmation.html')
    return template_c.render({}, request)

#@login_required
def ajouter_au_panier(request, plat_id):
    plat = Dish.objects.get(id=plat_id)
    panier, created = Panier.objects.get_or_create(utilisateur=request.user)

    item, created = ItemPanier.objects.get_or_create(panier=panier, plat=plat)

    if not created:
        item.quantite += 1
        item.save()

    return redirect('home')

#@login_required
def panier_view(request):
    try:
        panier = Panier.objects.get(utilisateur=request.user)
    except Panier.DoesNotExist:
        panier = None
    context = {
        'panier': panier,
    }
    return render(request, 'panier.html', context)

#@login_required
def retirer_du_panier(request, item_id):
    item = ItemPanier.objects.get(id=item_id)
    item.delete()
    return redirect('panier')

#@login_required
def home(request):
    # Récupérer tous les plats de la base de données
    plats = Dish.objects.all()  # Assurez-vous d'avoir un modèle Plat défini

    # Préparer le contexte à envoyer à la template
    context = {
        'plats': plats,
        'message_bienvenue': "Bienvenue dans notre restaurant !",
    }
    template = loader.get_template("resto/home.html")
    # Rendre la template 'home.html' avec le contexte
    return HttpResponse(template.render(context, request))

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(request, "Inscription réussie !")
            return redirect('login')
    else:
        form = RegistrationForm()
        
    #template_re = loader.get_template("resto/register.html")
    #return template_re.render({"form":form}, request)
    return render(request, "resto/register.html", {"form":form})

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Identifiants invalides.")
            
    template_lo = loader.get_template("resto/login.html")
    return HttpResponse(template_lo.render({}, request))

#@login_required
def reserve_table(request):
    if request.method == "POST":
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)  # Créer une réservation mais ne pas encore la sauvegarder
            reservation.user = request.user  # Associer la réservation à l'utilisateur connecté
            reservation.save()  # Sauvegarder la réservation en base de données
            messages.success(request, "Votre réservation a été enregistrée avec succès !")
            return redirect('home')  # Rediriger vers la page d'accueil ou une page de confirmation
    else:
        form = ReservationForm()
    
    template_re = loader.get_template("resto/reserve.html")
    return HttpResponse(template_re.render({}, request))

from django.shortcuts import get_object_or_404

#@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    if request.method == "POST":
        reservation.delete()
        messages.success(request, "Réservation annulée avec succès.")
        return redirect('home')

    template_cc = loader.get_template("resto/cancel_reservation.html")
    return HttpResponse(template_cc.render({}, request, {'reservation': reservation}))

#@login_required
def checkout(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        panier = Panier.objects.get(utilisateur=request.user)
        montant_total = sum(item.plat.price * item.quantite for item in panier.items.all())
        if request.method == 'POST':
        # Les détails de paiement à envoyer à l'API Orange Money
        # Remplacez les valeurs par vos propres informations
            url = 'https://api.orange.com/money/v1/requests'
            headers = {
                'Authorization': f'Bearer {settings.ORANGE_MONEY_API_TOKEN}',
                'Content-Type': 'application/json'
            }
            data = {
                "amount": montant_total,
                "currency": "FCFA",  # Ou votre devise
                "phoneNumber": request.POST.get('phoneNumber'),
                "description": "Paiement pour la commande",
            }

            response = requests.post(url, json=data, headers=headers)

            if response.status_code == 200:
                # Traitement à faire après le succès du paiement
                # Par exemple, enregistrer la commande
                panier.delete()  # Vider le panier après le paiement
                return redirect('confirmation')  # Page de confirmation

            else:
                # Gérer les erreurs
                context = {'error_message': 'Erreur lors du paiement, veuillez réessayer.'}
                return render(request, 'checkout.html', context)

        context = {
            'panier': panier,
            'montant_total': montant_total,
        }
        template_check = loader.get_template("resto/checkout.html")
        return template_check.render({}, request)
    else:
        return redirect('login')