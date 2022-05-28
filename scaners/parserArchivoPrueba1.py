

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
        while self.currentToken in ['anus2', 'numero', 'anus5']:
        	if self.currentToken in ['anus2', 'numero', 'anus5']:
        		self.Instruccion()
        		if self.currentToken == "anus0":
        			self.coincidir("anus0")

    def Instruccion(self):
        resultado = 0
        resultado = self.Expresion(resultado)
        print(resultado)

    def Expresion(self, resultado):
        resultado1 = 0;  resultado2 = 0
        resultado1 = self.Termino(resultado1)
        while self.currentToken in ['anus1', 'anus2']:
        	if self.currentToken == "anus1":
        		self.coincidir("anus1")
        		resultado2 = self.Termino(resultado2)
        		resultado1 += resultado2
        	else:
        		if self.currentToken == "anus2":
        			self.coincidir("anus2")
        			resultado2 = self.Termino(resultado2)
        			resultado1 -= resultado2
        resultado = resultado1
        return resultado

    def Termino(self, resultado):
        resultado1 = 0;  resultado2 = 0
        resultado1 = self.Factor(resultado1)
        while self.currentToken in ['anus3', 'anus4']:
        	if self.currentToken == "anus3":
        		self.coincidir("anus3")
        		resultado2 = self.Factor(resultado2)
        		resultado1 *= resultado2
        	else:
        		if self.currentToken == "anus4":
        			self.coincidir("anus4")
        			resultado2 = self.Factor(resultado2)
        			resultado1 /= resultado2
        resultado = resultado1
        return resultado

    def Factor(self, resultado):
        signo = 1
        if self.currentToken in ['anus2']:
        	if self.currentToken == "anus2":
        		self.coincidir("anus2")
        		signo = -1
        if self.currentToken in ['numero']:
        	resultado = self.Number(resultado)
        else:
        	if self.currentToken == "anus5":
        		self.coincidir("anus5")
        		resultado = self.Expresion(resultado)
        		if self.currentToken == "anus6":
        			self.coincidir("anus6")
        resultado *= signo
        return resultado

    def Number(self, resultado):
        if self.currentToken == "numero":
        	self.coincidir("numero")
        	resultado = float(self.lastvalue)
        	return resultado