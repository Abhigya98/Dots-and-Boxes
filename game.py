from tkinter import *
import numpy as np
import pandas as pd
from openpyxl import load_workbook

size_of_board = 400
number_of_dots = 5
symbol_size = (size_of_board / 3 - size_of_board / 8) / 2
symbol_thickness = 50
dot_color = '#7BC043'
player1_color = '#0492CF'
player1_color_light = '#67B0CF'
player2_color = '#EE4035'
player2_color_light = '#EE7E77'
Green_color = '#7BC043'
dot_width = 0.25*size_of_board/number_of_dots
edge_width = 0.1*size_of_board/number_of_dots
distance_between_dots = size_of_board / (number_of_dots)
res=0

class Dots_and_Boxes():

    # ------------------------------------------------------------------
    # Initialization functions
    # ------------------------------------------------------------------
    def __init__(self):
        self.window = Tk()
        self.window.title('Dots_and_Boxes')
        self.canvas = Canvas(self.window, width=size_of_board, height=size_of_board)
        self.canvas.pack()
        self.window.bind('<Button-1>', self.click)
        self.player1_starts = True
        self.refresh_board()
        self.play_again()
        self.df = pd.read_excel('stats.xlsx',index_col=0)
        if self.df.empty:
            self.df = pd.DataFrame({'Player 1': [], 'Player 2': [],'Res': [],'Date':[],'Time':[],'Timediff':[]})
        #self.lb= pd.read_excel('leaderboard.xlsx',index_col=0)
        #if self.lb.empty:
        self.lb = pd.DataFrame({'Name': [], 'Score': [],'Match no': [],'Wins':[],'Shortest Time':[],'Win%':[]})
        
        
    def append_dataset(self,x,y,z,d,t,tdiff):
        temp_df=pd.DataFrame({'Player 1': [x], 'Player 2': [y],'Res': [z],'Date':[d],'Time':[t],'Timediff':[float(tdiff)]})
        self.df=self.df.append(temp_df,sort=False)
        self.df.to_excel('stats.xlsx')


    def leaderboard(self):
        self.df = pd.read_excel('stats.xlsx',index_col=0)
        name=self.df['Player 1'].tolist()
        names=self.df['Player 2'].tolist()
        for i in range(len(self.df['Player 1'])):
            if name[i] not in self.lb['Name'].tolist():
                temp_lb=pd.DataFrame({'Name':[name[i]],'Score':[0],'Match no':[1],'Wins':[0],'Shortest Time':[999],'Win%':[0]})
                self.lb=self.lb.append(temp_lb,sort=False)
            else:
                self.lb.loc[self.lb['Name']==name[i],'Match no']+=1
            if self.df['Res'].values[i]==1:
                self.lb.loc[self.lb['Name']==name[i],'Score']+=1
                self.lb.loc[self.lb['Name']==name[i],'Wins']+=1
                if float(self.df['Timediff'].values[i])<float(self.lb.loc[self.lb['Name']==name[i],'Shortest Time']):
                    self.lb.loc[self.lb['Name']==name[i],'Shortest Time']=self.df['Timediff'].values[i]
            elif self.df['Res'].values[i]==0:
                self.lb.loc[self.lb['Name']==name[i],'Score']+=0.5
            self.lb.loc[self.lb['Name']==name[i],'Win%']=float(self.lb.loc[self.lb['Name']==name[i],'Wins'])/float(self.lb.loc[self.lb['Name']==name[i],'Match no'])*100

        for i in range(len(self.df['Player 2'])):
            if names[i] not in self.lb['Name'].tolist():
                temp_lb=pd.DataFrame({'Name':[names[i]],'Score':[0],'Match no':[1],'Wins':[0],'Shortest Time':[999],'Win%':[0]})
                self.lb=self.lb.append(temp_lb,sort=False)
            else:
                self.lb.loc[self.lb['Name']==names[i],'Match no']+=1
            if self.df['Res'].values[i]==2:
                self.lb.loc[self.lb['Name']==names[i],'Score']+=1
                self.lb.loc[self.lb['Name']==names[i],'Wins']+=1
                if float(self.df['Timediff'].values[i])<float(self.lb.loc[self.lb['Name']==names[i],'Shortest Time']):
                    self.lb.loc[self.lb['Name']==names[i],'Shortest Time']=self.df['Timediff'].values[i]
            elif self.df['Res'].values[i]==0:
                self.lb.loc[self.lb['Name']==names[i],'Score']+=0.5
            self.lb.loc[self.lb['Name']==names[i],'Win%']=float(self.lb.loc[self.lb['Name']==names[i],'Wins'])/float(self.lb.loc[self.lb['Name']==names[i],'Match no'])*100

        self.lb.sort_values(by=['Win%','Score','Match no','Shortest Time'],inplace=True,ascending=(False,False,False,True))
        #print(self.lb)
        self.lb.to_excel('leaderboard.xlsx')
        
    def play_again(self):
        self.refresh_board()
        self.board_status = np.zeros(shape=(number_of_dots - 1, number_of_dots - 1))
        self.row_status = np.zeros(shape=(number_of_dots, number_of_dots - 1))
        self.col_status = np.zeros(shape=(number_of_dots - 1, number_of_dots))
        
        # Input from user in form of clicks
        self.player1_starts = not self.player1_starts
        self.player1_turn = not self.player1_starts
        self.reset_board = False
        self.turntext_handle = []

        self.already_marked_boxes = []
        self.display_turn_text()

    def mainloop(self):
        self.window.mainloop()

    # ------------------------------------------------------------------
    # Logical Functions:
    # The modules required to carry out game logic
    # ------------------------------------------------------------------

    def is_grid_occupied(self, logical_position, type):
        r = logical_position[0]
        c = logical_position[1]
        occupied = True

        if type == 'row' and self.row_status[c][r] == 0:
            occupied = False
        if type == 'col' and self.col_status[c][r] == 0:
            occupied = False

        return occupied

    def convert_grid_to_logical_position(self, grid_position):
        grid_position = np.array(grid_position)
        position = (grid_position-distance_between_dots/4)//(distance_between_dots/2)

        type = False
        logical_position = []
        if position[1] % 2 == 0 and (position[0] - 1) % 2 == 0:
            r = int((position[0]-1)//2)
            c = int(position[1]//2)
            logical_position = [r, c]
            type = 'row'
            # self.row_status[c][r]=1
        elif position[0] % 2 == 0 and (position[1] - 1) % 2 == 0:
            c = int((position[1] - 1) // 2)
            r = int(position[0] // 2)
            logical_position = [r, c]
            type = 'col'

        return logical_position, type

    def mark_box(self):
        boxes = np.argwhere(self.board_status == -4)
        for box in boxes:
            if list(box) not in self.already_marked_boxes and list(box) !=[]:
                self.already_marked_boxes.append(list(box))
                color = player1_color_light
                self.shade_box(box, color)

        boxes = np.argwhere(self.board_status == 4)
        for box in boxes:
            if list(box) not in self.already_marked_boxes and list(box) !=[]:
                self.already_marked_boxes.append(list(box))
                color = player2_color_light
                self.shade_box(box, color)

    def update_board(self, type, logical_position):
        r = logical_position[0]
        c = logical_position[1]
        val = 1
        if self.player1_turn:
            val =- 1

        if c < (number_of_dots-1) and r < (number_of_dots-1):
            self.board_status[c][r] += val

        if type == 'row':
            self.row_status[c][r] = 1
            if c >= 1:
                self.board_status[c-1][r] += val

        elif type == 'col':
            self.col_status[c][r] = 1
            if r >= 1:
                self.board_status[c][r-1] += val

    def is_gameover(self):
        return (self.row_status == 1).all() and (self.col_status == 1).all()

    # ------------------------------------------------------------------
    # Drawing Functions:
    # The modules required to draw required game based object on canvas
    # ------------------------------------------------------------------

    def make_edge(self, type, logical_position):
        if type == 'row':
            start_x = distance_between_dots/2 + logical_position[0]*distance_between_dots
            end_x = start_x+distance_between_dots
            start_y = distance_between_dots/2 + logical_position[1]*distance_between_dots
            end_y = start_y
        elif type == 'col':
            start_y = distance_between_dots / 2 + logical_position[1] * distance_between_dots
            end_y = start_y + distance_between_dots
            start_x = distance_between_dots / 2 + logical_position[0] * distance_between_dots
            end_x = start_x

        if self.player1_turn:
            color = player1_color
        else:
            color = player2_color
        self.canvas.create_line(start_x, start_y, end_x, end_y, fill=color, width=edge_width)

    def display_gameover(self):
        player1_score = len(np.argwhere(self.board_status == -4))
        player2_score = len(np.argwhere(self.board_status == 4))

        if player1_score > player2_score:
            # Player 1 wins
            text = 'Winner: ' + Player1 
            color = player1_color
            res=1
        elif player2_score > player1_score:
            text = 'Winner:' + Player2 
            color = player2_color
            res=2
        else:
            text = 'Its a tie'
            color = 'gray'
            res=0
        x=pd.datetime.now()
        d=str(x.day)+'/'+str(x.month)+'/'+str(x.year)
        t=str(x.hour)+':'+str(x.minute)
        tdiff=(x-d1).seconds
        self.append_dataset(Player1,Player2,res,d,t,tdiff)
        
        self.canvas.delete("all")
        self.canvas.create_text(size_of_board / 2, size_of_board / 3, font="cmr 60 bold", fill=color, text=text)

        score_text = 'Scores \n'
        self.canvas.create_text(size_of_board / 2, 5 * size_of_board / 8, font="cmr 40 bold", fill=Green_color,
                                text=score_text)

        score_text = Player1 + ': '  + str(player1_score) + '\n'
        score_text += Player2 + ': '  + str(player2_score) + '\n'
        # score_text += 'Tie                    : ' + str(self.tie_score)
        self.canvas.create_text(size_of_board / 2, 3 * size_of_board / 4, font="cmr 30 bold", fill=Green_color,
                                text=score_text)
        self.reset_board = True

        score_text = 'Click to play again \n'
        self.canvas.create_text(size_of_board / 2, 15 * size_of_board / 16, font="cmr 20 bold", fill="gray",
                                text=score_text)

    def refresh_board(self):
        for i in range(number_of_dots):
            x = i*distance_between_dots+distance_between_dots/2
            self.canvas.create_line(x, distance_between_dots/2, x,
                                    size_of_board-distance_between_dots/2,
                                    fill='gray', dash = (2, 2))
            self.canvas.create_line(distance_between_dots/2, x,
                                    size_of_board-distance_between_dots/2, x,
                                    fill='gray', dash=(2, 2))

        for i in range(number_of_dots):
            for j in range(number_of_dots):
                start_x = i*distance_between_dots+distance_between_dots/2
                end_x = j*distance_between_dots+distance_between_dots/2
                self.canvas.create_oval(start_x-dot_width/2, end_x-dot_width/2, start_x+dot_width/2,
                                        end_x+dot_width/2, fill=dot_color,
                                        outline=dot_color)

    def display_turn_text(self):
        text = 'Next turn: '
        if self.player1_turn:
            text += Player1
            color = player1_color
        else:
            text += Player2
            color = player2_color

        self.canvas.delete(self.turntext_handle)
        self.turntext_handle = self.canvas.create_text(size_of_board - 5*len(text),
                                                       size_of_board-distance_between_dots/8,
                                                       font="cmr 15 bold", text=text, fill=color)


    def shade_box(self, box, color):
        start_x = distance_between_dots / 2 + box[1] * distance_between_dots + edge_width/2
        start_y = distance_between_dots / 2 + box[0] * distance_between_dots + edge_width/2
        end_x = start_x + distance_between_dots - edge_width
        end_y = start_y + distance_between_dots - edge_width
        self.canvas.create_rectangle(start_x, start_y, end_x, end_y, fill=color, outline='')

    def display_turn_text(self):
        text = 'Next turn: '
        if self.player1_turn:
            text += Player1
            color = player1_color
        else:
            text += Player2
            color = player2_color

        self.canvas.delete(self.turntext_handle)
        self.turntext_handle = self.canvas.create_text(size_of_board - 5*len(text),
                                                       size_of_board-distance_between_dots/8,
                                                       font="cmr 15 bold",text=text, fill=color)

    def click(self, event):
        if not self.reset_board:
            grid_position = [event.x, event.y]
            logical_positon, valid_input = self.convert_grid_to_logical_position(grid_position)
            if valid_input and not self.is_grid_occupied(logical_positon, valid_input):
                self.update_board(valid_input, logical_positon)
                self.make_edge(valid_input, logical_positon)
                self.mark_box()
                self.refresh_board()
                self.player1_turn = not self.player1_turn

                if self.is_gameover():
                    # self.canvas.delete("all")
                    self.display_gameover()
                else:
                    self.display_turn_text()
        else:
            self.canvas.delete("all")
            self.play_again()
            self.reset_board = False

   
print("The Dots and Boxes Game")
#player_deet()
Player1 = input("Enter the names of the first player: ")
Player2 = input("Enter the names of the second player: ")
print("Switch to different window to play the game")
d1=pd.datetime.now()
game_instance = Dots_and_Boxes()
#game_instance.leaderboard()
game_instance.mainloop()
game_instance.leaderboard()

