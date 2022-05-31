

class AnaSintac():
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.currentToken = None
        self.nextToken = self.tokens[self.pos]
        self.next()
        self.lastvalue = None

        self.main()

    def coincidir(self, terminal):
        if self.currentToken == terminal:
            self.next()
        else:
            self.reportar('Error de sintaxis')

    def next(self):
        if self.pos - 1 < 0:
            self.lastvalue = None
        else:
            self.lastvalue = self.tokens[self.pos - 1][1]

        if self.nextToken == None:
            self.currentToken = None
        else:
            self.currentToken = self.nextToken[0]
        self.pos += 1

        if self.pos >= len(self.tokens):
            self.nextToken = None
        else:
            self.nextToken = self.tokens[self.pos]
        

    def reportar(self, msg):
        print(msg)

    def main(self):
        self.EstadoInicial()

    def EstadoInicial(self):
        while self.currentToken in ['numeroToken']:
        	if self.currentToken in ['numeroToken']:
        		self.Instruccion()
        		if self.currentToken == "anus0":
        			self.coincidir("anus0")

    def Instruccion(self):
        resultado = 0
        resultado = self.Expresion(resultado)
        print("Resultado: ", resultado)

    def Expresion(self, resultado):
        resultado1 = 0;  resultado2 = 0
        resultado1 = self.Termino(resultado1)
        while self.currentToken in ['anus1']:
        	if self.currentToken == "anus1":
        		self.coincidir("anus1")
        		resultado2 = self.Termino(resultado2)
        		resultado1 += resultado2; print("Término: ", resultado1)
        resultado = resultado1; print("Término: ", resultado)
        return resultado

    def Termino(self, resultado):
        resultado1 = 0;  resultado2 = 0
        resultado1 = self.Factor(resultado1)
        while self.currentToken in ['anus2']:
        	if self.currentToken == "anus2":
        		self.coincidir("anus2")
        		resultado2 = self.Factor(resultado2)
        		resultado1 *= resultado2; print("Factor: ", resultado1)
        resultado = resultado1; print("Factor: ", resultado)
        return resultado

    def Factor(self, resultado):
        resultado1 = 0
        resultado1 = self.Numero(resultado1)
        resultado = resultado1; print("Número: ", resultado)
        return resultado

    def Numero(self, resultado):
        if self.currentToken == "numeroToken":
        	self.coincidir("numeroToken")
        	resultado = float(self.lastvalue); print("Token: ", resultado)
        	return resultado