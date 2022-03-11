import myfunctions as mf
import thompson as th

menu_machines = """
Ingrese una opción del menú:
1. AFN por Thompson
"""


if __name__ == '__main__':
    regrex = input('Ingresa la expresión regular: ')

    nfa = th.NFA(regrex)

    string = input('Ingresa la cadena a evaluar: ')

    print('{}'.format('SI' if nfa.evaluate(string) else 'NO'))
    #print(reg)
    #th.andres_method(reg)
    #printPostOrder(th.andres_method(reg))
    # th.sintactic_tree(regrex)
    #print(mf.add_concatenation(regrex))
    #print('La expresión regular {} {} está correcta.'.format(regrex, '' if mf.validate_regrex(regrex) else 'no'))
    # b.*((b.a).(b.*a))