#constantes
porciones_por_persona= 2
porciones_por_queque= 10
huevos_por_queque=4
tazas_harina_por_queque=8
tazas_leche_por_queque=0.5

#entrada
numero_de_invitados=int(input("ingrese el número de invitados:"))

#proceso
tazas_de_harina_por_invitado= tazas_harina_por_queque/porciones_por_persona
huevos_por_invitado= huevos_por_queque/ porciones_por_persona
tazas_de_leche_por_invitado= tazas_leche_por_queque/porciones_por_persona
tazas_de_harina_necesario= tazas_de_harina_por_invitado*numero_de_invitados*porciones_por_persona
huevos_necesarios=huevos_por_invitado*numero_de_invitados*porciones_por_persona
tazas_de_leche_necesarios= tazas_de_leche_por_invitado* numero_de_invitados *porciones_por_queque

#salida
print("se requiere:", tazas_de_leche_necesarios,'tazas de leche')
print("se requiere:", tazas_de_harina_necesario,'tazas de harina')
print("se requiere:", huevos_necesarios,'huevos')
