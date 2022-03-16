import myfunctions as mf
import thompson as th
import subsets as sb
import direct as dr

menu_machines = """
Ingrese una opción del menú:
1. AFN por Thompson
2. AFN a AFD
3. AFD directo
"""

if __name__ == '__main__':
    af = None

    regrex = input('Ingresa la expresión regular: ')

    if not mf.validate_regrex(regrex):
        print('La expresión regular no es válida')
        exit()

    while True:
        try:
            print(menu_machines)
            option = int(input('Opción: '))
            if option < 1 or option > 3:
                raise ValueError
            break
        except ValueError:
            print('Opción inválida')

    if option == 1:
        af = th.NFA(regrex)
    elif option == 2:
        af = sb.Subsets(regrex)
    elif option == 3:
        af = dr.Direct(regrex)

    word = input('Ingresa la cadena a evaluar: ')

    print('{}'.format('SÍ' if af.evaluate(word) else 'NO'))
