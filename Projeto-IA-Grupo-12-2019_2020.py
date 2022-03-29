from ev3dev2.motor import MediumMotor, OUTPUT_A,OUTPUT_B,OUTPUT_D, MoveTank
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import ColorSensor
from ev3dev2.sound import Sound
import time

#DEFINIÇÃO DE SENSORES
sound=Sound()
sensor=ColorSensor(INPUT_1)
sensor.mode = 'COL-COLOR'
claw=MediumMotor(OUTPUT_B)
tank_drive=MoveTank(OUTPUT_A,OUTPUT_D)

#RED - X
#GREEN - -
#BLUE - +
#YELLOW - O

#FUNCOES MOVIMENTO--------------------------------------------------------

def open_claw():#abre a garra
    claw.on_for_rotations(50,2)

def close_claw(): #fecha a garra
    claw.on_for_rotations(-50,2)

def turn_right(): #vira 90 graus para a direira
    tank_drive.on_for_rotations(-50,50,1.87)
    tank_drive.on_for_rotations(50,50,0.15)

def turn_left(): #vira 90 graus para a esquerda
    tank_drive.on_for_rotations(50,-50,1.87)

def turn_back(): #vira 180 graus
    tank_drive.on_for_rotations(50,-50,2*(1.87))

def release_piece(): #larga a peça, e recua um pouco
    open_claw()
    tank_drive.on_for_rotations(-60,-60,0.25)

def espera(): #espera para ser colocado na posição correta
    time.sleep(5)

def move_unity(steps): #anda para a frente a dimensão de um espaço do tabuleiro
    for i in range (0,steps):
        tank_drive.on_for_rotations(85,85,3.95)

#FUNCOES LEITURA DE COR--------------------------------------------------------
def le_cor(): #devolve a cor
    colors=('unknown','black','blue','green','yellow','red','white','brown')
    return (colors[sensor.value()])

#FUNCOES DE JOGO--------------------------------------------------------

def cria_lista():
    lista=[] # a lista começa vazua
    while(True):
        tank_drive.on_for_rotations(90,90,1.5) #anda para a frente
        turn_left() #vira-se para a peça
        x=0
        cor=le_cor() #vai lendo a cor
        while(cor=='unknown' or cor=='black'): #até encontrar uma cor que não seja a preta
            tank_drive.on_for_rotations(30,30,0.1)
            x=x+1
            cor = le_cor() #atribuimos a cor lida
        if cor == 'red':
            lista.append('x') #colocamos um x na lista se for vermelha
        elif cor == 'green':
            lista.append('-') #colocamos um - na lista se for verde
        elif cor == 'blue':
            lista.append('+') #colocamos um x+na lista se for azul
        elif cor == 'brown' or cor == 'yellow':
            lista.append('o')#colocamos um o na lista se for amarela ou castanha (o sensor varia um pouco)
        tank_drive.on_for_rotations(30,30,-0.1*x)
        turn_right() 
        if cor == 'white': #se ler uma peça branca, significa que a lista chegou ao fim
            break
    print(lista)
    tank_drive.on_for_rotations(90,90,-1.5*(len(lista)+1)) #volta à posição original
    espera()
    return lista

def apanha_prox_peca(n): #sabendo que já foram colocadas n-1 peças, apanha a peça n
    tank_drive.on_for_rotations(90,90,1.5*n) #anda até estar ao lado da peça
    turn_left() #vira-se para estar de frente para a peça
    i = 0
    cor=le_cor()
    while(cor == 'unknown' or cor=='black'): #anda para a frente até ler uma cor que não seja preto
        i = i+1
        tank_drive.on_for_rotations(30,30,0.1)
        cor = le_cor()
    close_claw() #consegue ler a cor, portanto está perto o suficiente para agarrar a peça
    for j in range (0,i): #volta para trás
        tank_drive.on_for_rotations(30,30,-0.1)
    turn_right() #coloca-se paralelo ao tabuleiro
    tank_drive.on_for_rotations(90,90,-1.5*n) #volta á posição original
    espera()

def coloca_peca(x,y): #coloca a peça que tem agarrada na posição x,y do tabuleiro
    move_unity(y) #move-se ao longo do eixo do y
    turn_right() #vira para se mover ao longo do eixo x
    move_unity(x) #move-se ao longo do eixo do x
    tank_drive.on_for_rotations(50,-50,0.8) #vira-se 45 graus
    tank_drive.on_for_seconds(50,50,1) #avança um pouco para
    release_piece() #largar a peça no centro do quadrado
    tank_drive.on_for_seconds(-50,-50,1) #volta para trás
    tank_drive.on_for_rotations(-50,50,0.8) #realinha-se conforme os eixos
    turn_right() # vira para voltar para trás ao longo do eixo dos y
    move_unity(y) #move-se conforme o eixo dos y
    turn_right() #alinha-se para o eixo dos X
    move_unity(x) #move-se ao longo do eixo dos X, voltando à posiçao de partida
    turn_right() #vira para voltar a ficar virado para as peças, para agarrar
    espera()



#VERIFICAÇÂO DE PECAS--------------------------------------------------------

# n é o tamanho do board
def verifica_menos(board,n): #verifica se existe algum menos completo no tabuleiro, de lado n
    resultados = [] #guarda as posições da figura na lista resultados
    for row in range (0,n-2): #para cada linha até a linha 2
        for e in range(0,n): #vê os elementos coluna a coluna
            if (board[row][e] == '-'and board[row+1][e] == '-'): #se encontrar 2 menos na mesma linha
                resultados.append([row, e]) #adiciona os elementos à lista
                resultados.append([row+1,e])
                if (board[row+2][e]=='-'): #e se houver mais um depois, adiciona esse também, para fazer a figura de 3 peças
                    resultados.append([row+2,e])
                print ("Retirado conjunto - com ",len(resultados)," pecas" )
                sound.speak("Remove minus")
                return resultados
    for e in range (0,n): #agora verificamos apenas a coluna 3, para peças com tamanho 2, com peças nas ultimas 2 colunas
        if (board[3][e] == '-'and board[4][e] == '-'):
                resultados.append([4, e])
                resultados.append([3, e])
                sound.speak("Remove minus")
                return resultados
    return None #se não encontrar, devolve None

def verifica_x(board,n): #verifica se existe algum menos completo no tabuleiro, de lado n
    result = [] #guarda as posições da figura na lista resultados
    if(board [0][0] == 'x' and board[1][1] == 'x' and board[2][2] == 'x' and board[3][3] == 'x' and board[4][4] == 'x' and board[0][4] == 'x' and board[4][0] == 'x' and board[3][1] == 'x' and board[1][3] == 'x'):
        result.append([0,0]) #verifica se há um X grande, já que pode estar apenas numa posição, e adiciona as posições ao resultado
        result.append([1,1])
        result.append([2,2])
        result.append([3,3])
        result.append([4,4])
        result.append([3,1])
        result.append([1,3])
        result.append([0,4])
        result.append([4,0])
        sound.speak("Remove ex")
        print("remove X")
        return result
    for row in range (0,n-2): #não havendo um X grande, vamos procurar um pequeno, tentando encontrar a peça do canto superior esquerdo
        for e in range(0,n-2): #não precisamos de procurar as ultimas 2 linhas e 2 colunas, pois a posição superior esquerda nunca vai estar lá
            if board[row][e] == 'x'and board[row+1][e+1] == 'x' and board[row+2][e+2] == 'x' and board[row+2][e] == 'x' and board[row][e+2] == 'x':
                print ("Retirado conjunto x com centro em: ", [row+1,e+1]) #se houver alguma posição em que haja um X e haja nas 4 posições relativas á primeira 
                result.append([row,e])#juntamos as posições ao resultado
                result.append([row+1,e+1])
                result.append([row+2,e])
                result.append([row,e+2])
                result.append([row+2,e+2])
                sound.speak("Remove ex")
                return result
    return None #se não for encontrado, devolvemos None

def verifica_mais(board,n):#verifica se existe algum menos completo no tabuleiro, de lado n
    result = []#guarda as posições da figura na lista resultados
    if(board [2][0] == '+' and board[2][1] == '+' and board[2][2] == '+' and board[2][3] == '+' and board[2][4] == '+' and board[0][2] == '+' and board[1][2] == '+' and board[3][2] == '+' and board[4][2] == '+'):
        result.append([2,0]) #verifica se há um + grande, já que pode estar apenas numa posição, e adiciona as posições ao resultado
        result.append([2,1])
        result.append([2,2])
        result.append([2,3])
        result.append([2,4])
        result.append([0,2])
        result.append([1,2])
        result.append([3,2])
        result.append([4,2])
        sound.speak("Remove plus")
        return result
    for row in range (0,n-1): #não havendo um + grande, vamos procurar um pequeno, tentando encontrar a peça da esquerda
        for e in range(0,n-1):
            if board[row][e] == '+'and board[row+1][e] == '+' and board[row+2][e] == '+' and board[row+1][e+1] == '+' and board[row+1][e-1] == '+':
                print ("Retirado conjunto + com centro em: ", [row+1,e]) #se encontrar uma peça que seja +, verifica as posições relativas à peça esquerda, e se todas forem +, sabe que encontrei um + pequeno
                result.append([row,e]) #adiciona as peças á lista de resultados
                result.append([row+1,e])
                result.append([row+2,e])
                result.append([row+1,e+1])
                result.append([row+1,e-1])
                sound.speak("Remove plus")
                return result #devolve as posições onde a peça completa está
    return None #se não encontrou peça nenhuma, devolve None

def verifica_o(board,n): #verifica se existe alguma peçam 'O' completo no tabuleiro, de lado n
    result = [] #guarda as posições da figura na lista resultados
    if (board[0][0] == 'o' and board[0][1] == 'o' and board[0][2] == 'o' and board[0][3] == 'o' and board[0][4] == 'o' and board[1][4] == 'o' and board[2][4] == 'o' and board[3][4] == 'o' and board[4][4] == 'o' and board[4][3] == 'o' and board[4][2] == 'o' and board[4][1] == 'o' and board[4][0] == 'o' and board[3][0] == 'o' and board[2][0] == 'o' and board[1][0] == 'o'):
        result.append([0,0]) #como o O maior só pode estar numa posição, ele verifica essas posições, e se todas forem O, adiciona-as ao resultado e devolve isso
        result.append([0,1])
        result.append([0,2])
        result.append([0,3])
        result.append([0,4])
        result.append([1,4])
        result.append([2,4])
        result.append([3,4])
        result.append([4,4])
        result.append([4,3])
        result.append([4,2])
        result.append([4,1])
        result.append([4,0])
        result.append([3,0])
        result.append([2,0])
        result.append([1,0])
        sound.speak("Remove circle")
        return result
    for row in range(0,n-1): #sabendo que não há um O grande, procuramos apenas os pequenos
        for i in range(0,n-1):
            if board[row][i]=='o' and board[row+1][i]=='o' and board[row][i+1]=='o' and board[row+1][i+1]=='o' : #se encontra um O, assumimos que esse é o do canto superior esquerdo
                result.append([row,i]) #quando encontra, adiciona as posições à lista de resultados
                result.append([row+1,i])
                result.append([row,i+1])
                result.append([row+1,i+1])
                print(result)
                sound.speak("Remove circle")
                return result
    return None #se não encontrar nenhum, devolve None

def calc_score(num): #calcula o score, com base no número de peças
    return 2**num

def retira(verifica,board): #retira as peças do tabuleiro interno, tendo o tabuleiro e as peças a retirar
    if (verifica != None): #se o resultado não for none
        for e in verifica: #para todos os elementos da lista
            board[e[0]][e[1]] = "" #retira a peça
        score_update = calc_score(len(verifica)) #calcula quantos pontos se ganha ao retirar esse número de peças
        return (board,score_update) #devolve o tabuleiro e o número de pontos ganhos
    return (board, 0) #se não foi encontrado nenhuma figura, devolve o tabuleiro e 0 pontos ganhos

def verifica_completo(board,ultima_peca,n): #verifica se no tabuleiro existe alguma figura feita com a ultima peça colocada
    if ultima_peca == 'o':
        return retira(verifica_o(board,n),board) #verifica se tem o completo e retira-os
    elif ultima_peca == '+':
        return retira(verifica_mais(board,n),board) #verifica se tem + completo e retira-os
    elif ultima_peca == '-':
        return retira(verifica_menos(board,n),board) #verifica se tem - completo e retira-os
    elif ultima_peca == 'x':
        return retira(verifica_x(board,n),board) #verifica se tem X completo e retira-os

def imprime_tabuleiro(board): #função que imprime o tabuleiro no PC, para podermos ver no ecrã o estado do tabuleiro interno do robot
    rez = [[board[j][i] for j in range(len(board))] for i in range (len(board[0]))]
    print("\n")
    for row in rez:
        print (row)
	
	
#-----------------------HEURISTICAS------------------------------------------
def count_elements(lst): #conta o número de cada tipo de peça na lista de peças
    count1 = 0 #número de O
    count2 = 0 #número de X
    count3 = 0 #número de -
    count4 = 0 #número de +
    for e in range(len(lst)): #verifica todos os elementos da lista e adiciona o número conforme os elementos que lê
        if lst[e] == 'o':
            count1 = count1 + 1 
        elif lst[e] == 'x':
            count2 = count2 + 1
        elif lst[e] == '-':
            count3 = count3 + 1
        elif lst[e] == '+':
            count4 = count4 + 1        
    return (count1,count2,count3,count4) #devolve o número de cada tipo de elemento da lista

def big_X(board,lista, menos): #heuristica que dá prioridade a fazer X grandes
    score_total = 0 #o score inicial é 0
    jogadas = 0 #o número de jogadas inicial é 0, e é usado para saber quão distante está a próxima peça a ser buscada
    pos_x = [(0,0),(4,0),(0,4),(4,4),(1,1),(3,1),(1,3),(3,3),(2,2)] #posições reservadas a X
    index_x = 0
    pos_menos = [(1,0),(3,0),(2,0)] #posições reservadas a -
    index_menos = 0
    pos_mais = [(1,2),(3,2),(2,1),(2,3),(2,2)]#posições reservadas a +
    index_mais = 0
    pos_o = [(0,1),(0,2),(0,3),(4,1),(4,2),(4,3),(4,3),(4,2),(4,1)]#posições reservadas a O
    index_o = 0
    while(lista != []): #enquanto a lista tem peças vai jogando
        apanha_prox_peca(jogadas+1) #apanha a próxima peça na lista
        if lista[0]=='x': #se a peça for um X
            board[pos_x[index_x][0]][pos_x[index_x][1]] = 'x' #coloca um x na posição da lista de posições reservadas a x, no modelo interno
            coloca_peca(pos_x[index_x][0],pos_x[index_x][1]) #coloca a peça na posição do index
            if index_x == len(pos_x)-1: #se o indice chegou a ultima posição
                score_total += verifica_completo(board, lista[0],len(board))[1] #verifica se tem um X completo no tabuleiro, e se tiver, atualiza o score e retira as peças do tabuleiro interno
                index_x = 0 #recoloca o indice a 0
            else:
                index_x +=1 #se não chegou ao fim da lista, incrementa o indice e continua
        elif lista[0]=='-': #Se for um menos
            board[pos_menos[index_menos][0]][pos_menos[index_menos][1]] = '-' #coloca o menos na posição da lista de de posições reservadas no modelo interno
            coloca_peca(pos_menos[index_menos][0],pos_menos[index_menos][1]) #coloca a peça na posição do index
            menos -=1 #decrementa o número de menos, para depois verificar se é para fazer um - grande ou pequeno
            if index_menos == len(pos_menos)-1: #se o indice chegou a ultima posição
                score_total += verifica_completo(board, lista[0],len(board))[1] #atualiza o score e retira as peças
                if(menos == 2): #se temos apenas 2 peças menos na lista
                    index_menos = 1 #não colocamos no inicio do indice, mas na segunda posição, para fazer um - pequeno
                else:
                    index_menos = 0 #caso contrário vamos fazer um - grande
            else:
                index_menos +=1 #como não acabamos a peça, incrementamos um indice
        elif lista[0]=='+':
            board[pos_mais[index_mais][0]][pos_mais[index_mais][1]] = '+'
            coloca_peca(pos_mais[index_mais][0],pos_mais[index_mais][1]) #coloca a peça na posição do index
            if index_mais == len(pos_mais)-1: #se o indice chegou a ultima posição
                score_total += verifica_completo(board, lista[0],len(board))[1] #verifica se completou alguma peça, retira-as do tabuleiro interno e atualiza o score
                index_mais = 0 #vai voltara colocar a peça na próxima posição
            else:
                index_mais +=1 #não completou peça, portanto apenas incrementa o indice
        elif lista[0]=='o':
            board[pos_o[index_o][0]][pos_o[index_o][1]] = 'o'
            coloca_peca(pos_o[index_o][0],pos_o[index_o][1]) #coloca a peça na posição do index
            index_x +=1
        lista = lista[1:] #volta a jogar, mas sem a peça que colocou
        imprime_tabuleiro(board) #imprime o tabuleiro, para podermos ver o seu estado interno
        jogadas +=1 #incrementa as jogadas, para saber quão longe ir buscar a próxima peça
        print (score_total) #imprime o score atual
    return score_total #devolve o score final

def big_plus (board,lista):
    score_temp = 0 
    jogadas = 0 #variavel para saber quão longe ir buscar a próxima peça
    score_total = 0
    pos_o = [(0,3),(0,4),(1,4),(1,3),(3,4),(4,4),(4,3),(4,1),(1,0),(0,0),(0,1)] #posições onde pode colocar a peça 'o'
    index_o = 0 #variavel que indica em qual das posições vamos colocar a próxima peça
    pos_x = [(1,1),(3,1),(3,3),(1,3),(2,2)] #posições onde pode colocar a peça 'x'
    index_x = 0 #variavel que indica em qual das posições vamos colocar a próxima peça
    pos_mais_grande = [(2,0),(2,1),(0,2),(1,2),(2,3),(2,4),(3,2),(4,2), (2,2)] #posições onde pode colocar a peça 'm'
    index_mais_grande = 0 #variavel que indica em qual das posições vamos colocar a próxima peça
    pos_menos = [(4,0),(3,0)] #posições onde pode colocar a peça '-'
    index_menos = 0 #variavel que indica em qual das posições vamos colocar a próxima peça

    while lista != []: #enquando houver peças para colocar
        apanha_prox_peca(jogadas+1) #apanha a próxima peça não colocada
        print (lista) #mostra a lista
        if lista[0] == 'o': #se a peça oe 'O'
            if index_o >2: #se o indice for maior que 2
                index_o = 3 #assumimos que é 3, para verificar se há um espaço que antes não estava disponivel
                while board[pos_o[index_o][0]][pos_o[index_o][1]] != '': #procuramos a próxima posição da lista que não tem peça
                    index_o +=1
            board[pos_o[index_o][0]][pos_o[index_o][1]] = 'o' #colocamos na primeira posição livre no tabuleiro interno
            coloca_peca(pos_o[index_o][0],pos_o[index_o][1]) #colocamos a peça no tabuleiro
            index_o = index_o + 1 #incrementamos o indice
            if index_o > 3: #se for maior que 3, quer dizer que é possível que tenhamos completo uma figura
                temp= verifica_completo(board, lista[0],len(board))[1] #verificamos se há figura completa e atualizamos o score
                score_total += temp
                if temp != 0: #se o temp é 0, quer dizer que não fizemos figura. 
                    index_o = 0 #se não for 0, quer dizer que fizemos figura e voltamos com o indice ao inicio
            temp = 0 #voltamos a por temp a 0, para podermos fazer futuras verificações
            
        if lista[0] == 'x': #se a peça for x
            board[pos_x[index_x][0]][pos_x[index_x][1]] = 'x' #coloca no modelo interno
            coloca_peca(pos_x[index_x][0],pos_x[index_x][1]) #coloca no tabuleiro
            index_x = index_x + 1 #incrementamos a posição seguinte a colocar
            if index_x == len(pos_x): #se tivermos chegado ao fim da lista
                score_total += verifica_completo(board, lista[0],len(board))[1] #verificamos se há figuras completas, retiramos e atualizamos o score
                index_x = 0 #voltamos a por o indice a 0
       
        if lista[0] == '+':
            board[pos_mais_grande[index_mais_grande][0]][pos_mais_grande[index_mais_grande][1]] = '+'#coloca no modelo interno
            coloca_peca(pos_mais_grande[index_mais_grande][0],pos_mais_grande[index_mais_grande][1])#coloca no tabuleiro
            index_mais_grande = index_mais_grande + 1 #incrementamos a posição seguinte a colocar
            if index_mais_grande == (len(pos_mais_grande)) : #se tivermos chegado ao fim da lista
                score_total += verifica_completo(board, lista[0],len(board))[1]#verificamos se há figuras completas, retiramos e atualizamos o score
                index_mais_grande = 0  #voltamos a por o indice a 0
        
        if lista[0] == '-':
            board[pos_menos[index_menos][0]][pos_menos[index_menos][1]] = '-' #coloca no modelo interno
            coloca_peca(pos_menos[index_menos][0],pos_menos[index_menos][1])#coloca no tabuleiro
            index_menos = index_menos + 1 #incrementamos a posição seguinte a colocar
            if index_menos == len(pos_menos): #se tivermos chegado ao fim da lista
                score_total += verifica_completo(board, lista[0],len(board))[1] #verificamos se há figuras completas, retiramos e atualizamos o score
                index_menos = 0 #voltamos a por o indice a 0
                
        lista = lista[1:] #voltamos a jogar com a lista sem a peça colocada
        jogadas= jogadas + 1 #incrementamos o número de jogadas para saber quanto o robot tem de andar para buscar a próxima peça
        imprime_tabuleiro(board) #imprimimos a tabuleiro para podermos ver o estado do modelo interno
        print(score_total) #imprimimos o score até agora
    return score_total #devolvemos o score final

def big_O (board,lista,menos):
    score_total = 0 #guarda a pontuação
    jogadas = 0 #variavel para saber quão longe ir buscar a próxima peça
    pos_o = [(0,0),(0,1),(0,2),(0,3),(0,4),(1,0),(2,0),(3,0),(4,0),(4,1),(4,2),(4,3),(4,4),(1,4),(2,4),(3,4)] #posições onde pode colocar a peça 'o'
    index_o = 0 #variavel que indica em qual das posições vamos colocar a próxima peça
    pos_x = [(1,1),(1,3),(3,1),(3,3),(2,2)] #posições onde pode colocar a peça 'x'
    index_x = 0 #variavel que indica em qual das posições vamos colocar a próxima peça
    pos_mais = [(2,1),(1,2),(3,2),(2,3),(2,2)] #posições onde pode colocar a peça '+'
    index_mais = 0 #variavel que indica em qual das posições vamos colocar a próxima peça
    pos_menos = [(1,2),(3,2),(2,2)] #posições onde pode colocar a peça '-'
    index_menos = 0 #variavel que indica em qual das posições vamos colocar a próxima peça

    while lista != []: #enquanto houver peças, continua a jogar
        apanha_prox_peca(jogadas+1) #apanha a próxima peça a ser jogada
        print (lista)
        if lista[0] == 'o': #se a peça for o
            board[pos_o[index_o][0]][pos_o[index_o][1]] = 'o' #coloca no modelo interno na posição reservada
            coloca_peca(pos_o[index_o][0],pos_o[index_o][1]) #coloca no tabuleiro real
            index_o = index_o + 1 #atualiza o indice para a próxima posição a jogar
            if index_o == len(pos_o): #se tiver colocado na ultima posição do indice
                score_total += verifica_completo(board, lista[0],len(board))[1] #verifica se está a figura completa e atualiza o score e retira do modelo interno
                index_o = 0 #o indice volta a 0

        if lista[0] == 'x': #se a peça for x
            board[pos_x[index_x][0]][pos_x[index_x][1]] = 'x'#coloca no modelo interno na posição reservada
            coloca_peca(pos_x[index_x][0],pos_x[index_x][1]) #coloca no tabuleiro real
            index_x = index_x + 1 #atualiza o indice para a próxima posição a jogar
            if index_x == len(pos_x): #se tiver colocado na ultima posição do indice
                score_total += verifica_completo(board, lista[0],len(board))[1] #verifica se está a figura completa e atualiza o score e retira do modelo interno
                index_x = 0 #o indice volta a 0
        if (menos == 0): #se não houverem menos na lista, quer dizer que podemos colocar +
            if lista[0] == '+': #se a peça for +
                board[pos_mais[index_mais][0]][pos_mais[index_mais][1]] = '+' #coloca no modelo interno
                coloca_peca(pos_mais[index_mais][0],pos_mais[index_mais][1]) #coloca no tabuleiro real
                index_mais = index_mais + 1 #atualiza o indice
                if index_mais == len(pos_mais):  #se tiver colocado na ultima posição do indice
                    score_total += verifica_completo(board, lista[0],len(board))[1] #verifica se está a figura completa e atualiza o score e retira do modelo interno
                    index_mais = 0 #o indice volta a 0
        else: #se há menos na lista, não existem + para colocar
            if lista[0] == '-': #se a peça for -
                board[pos_menos[index_menos][0]][pos_menos[index_menos][1]] = '-'  #coloca no modelo interno
                coloca_peca(pos_menos[index_menos][0],pos_menos[index_menos][1])   #coloca no tabuleiro real
                index_menos = index_menos + 1 #atualiza o indice
                if index_menos == len(pos_menos): #se tiver chegado ao fim da lista
                    score_total += verifica_completo(board, lista[0],len(board))[1] #verifica se tem figura completa, e se tiver, retira do modelo interno e atualiza o score
                    index_menos = 0         #o indice volta ao inicio
                
        lista = lista[1:] #volta a jogar com a lista menos a peça colocada
        jogadas = jogadas + 1 #incrementa a distância a percorrer até encontrar a próxima peça
        imprime_tabuleiro(board) #imprime o tabuleiro para vermos o estado interno
        print(score_total) #imprime o score atual
    return score_total #devolve o score final

def big_Plus_X (board,lista):
    score_total = 0 #pontuação do jogo
    pos_o = [(1,0),(3,0),(4,3),(3,4),(1,4),(0,3),(0,1),(4,1)] #posições reservadas ao o e ao -
    index_o = 0
    pos_x = [(0,0),(4,0),(4,4),(0,4),(3,1),(3,3),(1,3),(1,1),(2,2)] #posições reservadas ao x
    index_x = 0
    pos_mais = [(2,0),(2,1),(2,3),(2,4),(3,2),(4,2),(0,2),(1,2),(2,2)] #posições reservadas ao +
    index_mais = 0
    jogadas = 0 #variavel para saber quanto o robot tem de andar para buscar a próxima peça
    while lista != []: #enquanto houver peças para jogar continua
        apanha_prox_peca(jogadas+1) #vai buscar a próxima peça a ser jogada
        print (lista) #imprime a lista para podermos ver o estado interno
        if lista[0] == 'o' or lista[0] == '-': #se a peça for o ou -
            board[pos_o[index_o][0]][pos_o[index_o][1]] = 'o' #coloca o no estado interno. Não nos preocupamos com o -, pois neste jogo não completamos figuras - ou o
            coloca_peca(pos_o[index_o][0],pos_o[index_o][1]) #colocamos no tabuleiro real
            index_o = index_o + 1 #atualizamos o indice

        if lista[0] == 'x': #se a peça for x
            board[pos_x[index_x][0]][pos_x[index_x][1]] = 'x' #colocamos no modelo interno
            coloca_peca(pos_x[index_x][0],pos_x[index_x][1]) #colocamos no tabuleiro real
            index_x = index_x + 1 #atualizamos o indice para colocarmos na próxima posição
            if index_x == len(pos_x): #se chegarmos ao fim da lista de posições 
                score_total += verifica_completo(board, lista[0],len(board))[1] #vemos se terminamos uma figura, e nesse caso retiramos do modelo interno e atualizamos o score
                index_x = 0 #o indice volta ao inicio
        if lista[0] == '+': #se a peça for +
            board[pos_mais[index_mais][0]][pos_mais[index_mais][1]] = '+'#colocamos no modelo interno
            coloca_peca(pos_mais[index_mais][0],pos_mais[index_mais][1])#colocamos no tabuleiro real
            index_mais = index_mais + 1 #atualizamos o indice para colocarmos na próxima posição
            if index_mais == len(pos_mais): #se chegarmos ao fim da lista de posições 
                score_total += verifica_completo(board, lista[0],len(board))[1]  #vemos se terminamos uma figura, e nesse caso retiramos do modelo interno e atualizamos o score
                index_mais = 0       #o indice volta ao inicio
        lista = lista[1:] #voltamos a jogar, mas sem a peça que foi colocada
        jogadas+=1 #incrementamos a distancia para a peça seguinte
        imprime_tabuleiro(board) #imprimimos o tabuleiro
        print(score_total) #e o score atual
    return score_total #devolvemos a pontuação final

def simples (board,lista,menos):
    score_total = 0
    jogadas = 0
    pos_o = [(0,3),(0,4),(1,4),(1,3)] #posições reservadas ao o
    index_o = 0
    pos_x = [(2,2),(4,2),(3,3),(4,2),(4,4)] #posições reservadas ao x
    index_x = 0
    pos_mais = [(3,0),(3,1),(3,2),(2,1),(4,1)] #posições reservadas ao +
    index_mais = 0
    pos_menos = [(0,0),(2,0),(1,0)] #posições reservadas ao -
    index_menos = 0
    while lista != []:   #enquanto houver peças para jogar continua
        apanha_prox_peca(jogadas+1) #apanha a próxima peça na lista
        print (lista)
        if lista[0] == 'o': #se a peça for o
            board[pos_o[index_o][0]][pos_o[index_o][1]] = 'o' #coloca no modelo interno
            coloca_peca(pos_o[index_o][0],pos_o[index_o][1]) #coloca no tabuleiro real
            index_o = index_o + 1
            if index_o == len(pos_o): #se tiver colocado na ultima posição
                score_total += verifica_completo(board, lista[0],len(board))[1] #verifica se tem uma figura completa, retira do modelo interno e atualiza o score
                index_o = 0 #o indice volta a 0
        if lista[0] == 'x':
            board[pos_x[index_x][0]][pos_x[index_x][1]] = 'x' #coloca no modelo interno
            coloca_peca(pos_x[index_x][0],pos_x[index_x][1]) #coloca no tabuleiro real
            index_x = index_x + 1
            if index_x == len(pos_x): #se tiver colocado na ultima posição
                score_total += verifica_completo(board, lista[0],len(board))[1] #verifica se tem uma figura completa, retira do modelo interno e atualiza o score
                index_x = 0
        if lista[0] == '+':
            board[pos_mais[index_mais][0]][pos_mais[index_mais][1]] = '+'#coloca no modelo interno
            coloca_peca(pos_mais[index_mais][0],pos_mais[index_mais][1]) #coloca no tabuleiro real
            index_mais = index_mais + 1
            if index_mais == len(pos_mais): #se tiver colocado na ultima posição
                score_total += verifica_completo(board, lista[0],len(board))[1] #verifica se tem uma figura completa, retira do modelo interno e atualiza o score
                index_mais = 0
        if lista[0] == '-':
            board[pos_menos[index_menos][0]][pos_menos[index_menos][1]] = '-'#coloca no modelo interno
            coloca_peca(pos_menos[index_menos][0],pos_menos[index_menos][1]) #coloca no tabuleiro real
            index_menos = index_menos + 1
            menos=menos-1
            if index_menos == len(pos_menos): #se tiver colocado na ultima posição
                score_total += verifica_completo(board, lista[0],len(board))[1] #verifica se tem uma figura completa, retira do modelo interno e atualiza o score
                index_menos = 0
                if(menos == 2): #se existirem apenas 2 -
                    index_menos = 1 #colocamos o indice a 1, para fazer um - pequeno
        imprime_tabuleiro(board) #imprime tabuleiro para vermos o estado interno
        lista = lista[1:] #volta a jogar, mas sem a peça colocada
        jogadas = jogadas + 1 #incrementa a distancia que tem de percorrer até a próxima peça
        print(score_total)
    return score_total #devolve a pontuação final do jogo

#JOGO_______________________________________________________________-----

def heuristica1(): #só joga com a heurisitica simples, independentemente das peças na lista
    #criação do board-------------
    board_size = 5 #o tabuleiro tem tamanho 5
    board=[] #e é representado por uma lista
    for x in range(0, board_size): #adiciona os espaços em branco ao tabuleiro
        board.append([''] * board_size) #adiciona os espaços em branco ao tabuleiro
    for i in range(board_size):
        for j  in range(board_size):
            board[i][j] = ''  #adiciona os espaços em branco ao tabuleiro
    imprime_tabuleiro(board)
    pecas = cria_lista() #vemos que peças temos para jogar
    (o,x, menos, mais) = count_elements(pecas) #e contamos o número de peças
    print ("simple")
    sound.speak("simple") #o robot diz que heuristica vai usar
    score =simples(board,pecas,menos) #joga a heuristica e fica com o score final
    sound.speak("I got "+str(score)+ "points") #diz qual a pontuação final


def heuristica2(): #escolhe a heuristica, dependendo da lista que peças

    #criação do board-------------
    board_size = 5 #o tabuleiro tem tamanho 5
    board=[] #e é representado por uma lista
    for x in range(0, board_size): #adiciona os espaços em branco ao tabuleiro
        board.append([''] * board_size) #adiciona os espaços em branco ao tabuleiro
    for i in range(board_size):
        for j  in range(board_size):
            board[i][j] = ''  #adiciona os espaços em branco ao tabuleiro
    imprime_tabuleiro(board)
    pecas = cria_lista() #vemos que peças temos para jogar
    (o,x, menos, mais) = count_elements(pecas) #e contamos o número de peças
    if(o >= 16 and (menos == 0 or mais == 0)): #se temos o suficientes para um o grande e não temos + ou não temos - usamos a heuristica big_O
        print ("big O")
        sound.speak("big o")
        score = big_O(board,pecas,menos)
    elif((o + menos)<9 and mais > 8 and x > 8): #se temos menos de 9 o e -, e muitos X e +, usamos a heuristica big_Plus_X
        print ("big + x")
        sound.speak("big plus big x")  
        score =big_Plus_X(board,pecas) #joga a heuristica e fica com o score final
    elif(mais>= 9 and x<= 8): #se temos muitos mais e poucos X, usamos a heuristica big_plus
        print ("big +")
        sound.speak("big plus")
        score =big_plus(board,pecas) #joga a heuristica e fica com o score final
    elif(x>=9 and mais<= 8 and o<= 9): #se temos muitos X, poucos + e poucos o, usamos a heuristica big_X
        print ("big x")
        sound.speak("big x")
        score =big_X(board,pecas,menos) #joga a heuristica e fica com o score final
    else: #se não se enquadrar em nenhuma das heuristicas acima, usamos a mais simples
        print ("simple")
        sound.speak("simple")
        score =simples(board,pecas,menos) #joga a heuristica e fica com o score final
    
    sound.speak("I got "+str(score)+ "points") # no final diz quantos pontos fez

