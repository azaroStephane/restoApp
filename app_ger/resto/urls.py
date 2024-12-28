from django.urls import path
from .views import home, login_view, register, checkout, reserve_table, cancel_reservation, ajouter_au_panier, panier_view, retirer_du_panier, confirmation

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('checkout/', checkout, name='checkout'),
    path('confirmation/', confirmation, name='confirmation'),
    path('reserve/', reserve_table, name='reserve'),
    path('cancel/<int:reservation_id>/', cancel_reservation, name='cancel_reservation'),
    path('ajouter-au-panier/<int:plat_id>/', ajouter_au_panier, name='ajouter_au_panier'),
    path('panier/', panier_view, name='panier'),
    path('retirer-du-panier/<int:item_id>/', retirer_du_panier, name='retirer_du_panier'),
]
