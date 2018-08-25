#Main module.

import tkinter as tk
import numpy as np
from scipy.sparse.linalg import eigsh
import scipy.sparse as spa
image_path = 'Images/'

#Grid start coordinates, grid spacings and number of grid squares.
x_start = 20
y_start = 20
dx_grid = 65
dy_grid = 65
x_number = 12
y_number = 6

#Initial spin position
spin_posx_init = 900
spin_posy_init = 150

#Canvas Size.
canvas_width = 1000
canvas_height = 500

#Spin matrices and identity matrix.
I2 = spa.bsr_matrix(np.eye(2))
Sx = spa.bsr_matrix([[0,0.5],[0.5,0]])
Sy = spa.bsr_matrix([[0,0.5*1j],[-0.5*1j,0]])
Sz = spa.bsr_matrix([[0.5,0],[0,-0.5]])

#J-value.
J = 1

#Spin Image.
spin_type = 'Test.gif'
spin_raised = 'Spin_Raised.gif'
spin_sunken = 'Spin_Sunken.gif'


#################Calculation Functions###########################


#Creates matrix for a particular set of spins. N: Total number of spins.
def Create_Int(spin1,spin2,N):
    Int_Matx = 1
    Int_Maty = 1
    Int_Matz = 1
    for i in range(spin1):
        Int_Matx = spa.kron(Int_Matx,I2)
        Int_Maty = spa.kron(Int_Maty,I2)
        Int_Matz = spa.kron(Int_Matz,I2)
    
    Int_Matx = spa.kron(Int_Matx,Sx)
    Int_Maty = spa.kron(Int_Maty,Sy)
    Int_Matz = spa.kron(Int_Matz,Sz)
    
    diff = spin2 - spin1
    for i in range(diff-1):
        Int_Matx = spa.kron(Int_Matx,I2)
        Int_Maty = spa.kron(Int_Maty,I2)
        Int_Matz = spa.kron(Int_Matz,I2)
    
    Int_Matx = spa.kron(Int_Matx,Sx)
    Int_Maty = spa.kron(Int_Maty,Sy)
    Int_Matz = spa.kron(Int_Matz,Sz)   
    
    for i in range(N-1-spin2):
        Int_Matx = spa.kron(Int_Matx,I2)
        Int_Maty = spa.kron(Int_Maty,I2)
        Int_Matz = spa.kron(Int_Matz,I2)        
    
    Int = Int_Matx + Int_Maty + Int_Matz
    return Int

#############Main UI#################

class Spin_Object(object):
    def __init__(self, spin_type, xpos, ypos):
        self.xpos, self.ypos = xpos, ypos
        self.spin_type = spin_type
        
        #Spin ID number.
        self.spin_number = main_canvas.spin_count
        
        #Set spin status (Locked: Due to interaction arrow, need to lock the spin. -- 0 is unlocked.)
        self.lock_status = 0
        
        #Create image.
        self.spin_image = tk.PhotoImage(
            file = '{}{}'.format(image_path, spin_type))
        
        self.spin = main_canvas.create_image(
            xpos, ypos, image = self.spin_image)
        
        #On click, create a new spin at the back.
        main_canvas.tag_bind(self.spin, '<Button-1>', self.createnew)        

    def createnew(self, event):
        x_init, y_init = main_canvas.coords(self.spin)
         
        #If starting position of the spin is at its original position, create a new spin.
        if  (x_init == self.xpos and 
             y_init == self.ypos):
        
            #First add a count to spin number.
            main_canvas.spin_count += 1
        
            #Then create the spin.     
            main_canvas.spin_list.append(Spin_Object(
                self.spin_type, self.xpos, self.ypos))        
            
        #Assigning the initial click position to an attribute.
        self.x = event.x
        self.y = event.y
        
        #Moving the spin.
        main_canvas.tag_bind(self.spin, '<Button1-Motion>', 
                             self.startmove)
        #End moving the spin, delete the 2nd spin if necessary.
        main_canvas.tag_bind(self.spin, '<ButtonRelease-1>', self.endmove)    

    def startmove(self, event):
        
        print('{0}'.format(self.lock_status))
        
        if self.lock_status == 0:
            #Calculating how much to move the spin.
            rel_xpos = event.x - self.x
            rel_ypos = event.y - self.y
        
            #Updating the start motion value.
            self.x, self.y = event.x, event.y
        
            main_canvas.move(self.spin, rel_xpos, rel_ypos)
            
        else:
            self.error_lock_window = tk.Toplevel()
            self.error_lock = tk.Label(self.error_lock_window, 
                               text = 'Error!\nSpin is linked via an interaction.\nPlease remove interaction arrow first.')
            self.error_lock.grid(row = 0, column = 0)
        
    def endmove(self, event):
        final_x, final_y = main_canvas.coords(self.spin)
         
        #Code in if cycle is to snap the spin to grid.
        #If spin is outside of grid lines, return it to the original position
        if (final_x > main_canvas.grid_xlines[-1] or 
            final_y > main_canvas.grid_ylines[-1]):
            
            x_spot = self.xpos
            y_spot = self.ypos
            
        elif (final_x < main_canvas.grid_xlines[0]):
            
            #Return it to the first column if spin is outside first column.
            x_spot = main_canvas.grid_xlines[0] + dx_grid / 2
            
            if (final_y < main_canvas.grid_ylines[0]):
                
                #If spin is at top left corner, but outside grid, move it to 1st square.
                y_spot = main_canvas.grid_ylines[0] + dx_grid / 2  
            
            else:
                #Find the square the spin should be placed in.
                y_vec = [y for y in main_canvas.grid_ylines if y >= final_y]
                y_spot = y_vec[0] - dy_grid / 2
              
        elif (final_y < main_canvas.grid_ylines[0]):
            
            y_spot = main_canvas.grid_ylines[0] + dy_grid / 2
            
            #Find square which the spin should be placed in.
            x_vec = [x for x in main_canvas.grid_xlines if x >= final_x]
            x_spot = x_vec[0] - dx_grid / 2
        
        else:
            #Find correct box.
            x_vec = [x for x in main_canvas.grid_xlines if x >= final_x]
            x_spot = x_vec[0] - dx_grid / 2      
            y_vec = [y for y in main_canvas.grid_ylines if y >= final_y]
            y_spot = y_vec[0] - dy_grid / 2                               

        #Find relative amount to move spin by.
        rel_xpos = x_spot - final_x
        rel_ypos = y_spot - final_y        
    
        #Move spin to new position.
        main_canvas.move(self.spin, rel_xpos, rel_ypos)
        
        #Check the positions of all other spins.
        for i in main_canvas.spin_list:
            spin_id = i.spin_number
            
            #Don't compare spin to itself.
            if spin_id != self.spin_number:
                x_init, y_init = main_canvas.coords(i.spin)
            
                #If have two spins on the same spot,
                if x_init == x_spot and y_init == y_spot:
                    
                    #Delete the spin (that is not moved) & change the spin_count.
                    main_canvas.delete(i.spin)
                    del main_canvas.spin_list[spin_id]
                    main_canvas.spin_count -= 1
                    
                    #Re-number all spins.
                    for j in range(0, len(main_canvas.spin_list)):
                        main_canvas.spin_list[j].spin_number = j


class Spin_Button(object):
    def __init__(self, spin_type, xpos, ypos, button_id):
        self.id = button_id
        self.xpos, self.ypos = xpos, ypos
        
        #Create image of spin.
        self.spin_raised = tk.PhotoImage(
            file = '{}{}'.format(image_path, spin_raised))
        self.spin_sunken = tk.PhotoImage(
            file = '{}{}'.format(image_path, spin_sunken))
        
        #Create the button on canvas.
        self.sp_button = main_canvas.create_image(
            xpos, ypos, image = self.spin_raised, tag = 'sp_button')
        
        main_canvas.tag_bind(self.sp_button, '<Button-1>', self.activate)
    
    
    def activate(self,event):
        print(main_canvas.link_status)
        print(self.id)
        #If no spin is clicked yet.
        if main_canvas.link_status == -1:
            
            #Then set link status to active (Own ID).
            main_canvas.link_status = self.id
            
            #Sink & change button background.
            main_canvas.itemconfig(self.sp_button, image = self.spin_sunken)

        
        #If select the same spin again while activated.
        elif main_canvas.link_status == self.id:
            #Lift the button up & reset link status.
            main_canvas.itemconfig(self.sp_button, image = self.spin_raised)
            main_canvas.link_status = -1
            
        #If one spin is already clicked.
        else:
            
            #Reset the spin buttons to raised states.
            main_canvas.itemconfig(main_canvas.s_button_list[main_canvas.link_status].sp_button,
                image = self.spin_raised)
            
            #Add in spin arrows.
            main_canvas.int_list.append(Int_Arrow(
                self.xpos, self.ypos, main_canvas.s_button_list[main_canvas.link_status].xpos,
                main_canvas.s_button_list[main_canvas.link_status].ypos))
            
            #Lock spins.
            main_canvas.spin_list[main_canvas.link_status].lock_status += 1
            main_canvas.spin_list[self.id].lock_status += 1
            
            #Reset spin list status to no clicked spin.
            main_canvas.link_status = -1

class Int_Arrow(object):
    def __init__(self, xpos1, ypos1, xpos2, ypos2):
        #Retain interaction positions.
        self.xpos1 = xpos1
        self.xpos2 = xpos2
        self.ypos1 = ypos1
        self.ypos2 = ypos2
        
        #Get the positions of the spin buttons.
        xpos_left, xpos_right = min(xpos1, xpos2), max(xpos1, xpos2)
        ypos_down, ypos_up = min(ypos1, ypos2), max(ypos1, ypos2)
        
        if ((xpos1 == xpos_left and ypos1 == ypos_up) or 
            (xpos1 == xpos_right and ypos1 == ypos_down)):
            switch = 0
            
        else:
            switch = 1
        
        #Check for error: If spins are too close, can't draw arrow.
        if (((xpos_right == xpos_left + dx_grid) or xpos_right == xpos_left) and 
            ((ypos_down == ypos_up + dy_grid) or ypos_down == ypos_up)):
            
            #Put up error message.
            self.Error_Close_Msg()
            
            #Delete the interaction term created.
            main_canvas.int_list.pop()
            
        else:
      
            if xpos_left + dx_grid >= xpos_right :
                xpos_left = xpos_left + dx_grid / 2
                xpos_right = xpos_right - dx_grid / 2

            if ypos_up + dy_grid >= ypos_down:
                ypos_down = ypos_down + dy_grid / 2
                ypos_up = ypos_up - dy_grid / 2
                
        if switch == 1:
            #Switch to match spin coordinates.
            y_temp = ypos_up
            ypos_up = ypos_down
            ypos_down = y_temp    
            
        #Creates arrow and binds key to delete the particular interaction.
        self.arrow = main_canvas.create_line(xpos_left, ypos_up, xpos_right, ypos_down,
                                             arrow = tk.BOTH, arrowshape = (5,5,5), width = 3)
        main_canvas.tag_bind(self.arrow, '<Button-1>', self.delete_popup)
        
    def delete_popup(self,event):
        self.del_query = tk.Toplevel()
        
        self.query_msg = tk.Label(self.del_query, text = 'Confirm delete?')
        self.query_msg.grid(row = 0, column = 0)

        yes_button = tk.Button(self.del_query, text = 'Yes', command = self.delete)
        yes_button.grid(row = 1, column = 0)
        
        no_button = tk.Button(self.del_query, text = 'No', command = self.resume)
        no_button.grid(row = 1, column = 1)       

    def delete(self):
        #Close message.
        self.del_query.destroy()
        
        #Delete Interaction Arrow.
        main_canvas.delete(self.arrow)
        
        #Delete corresponding term in int_list.
        z = -1;
        for j in main_canvas.int_list:
            xint1, yint1 = j.xpos1, j.ypos1
            xint2, yint2 = j.xpos2, j.ypos2
            z += 1
            
            if xint1 == self.xpos1 and xint2 == self.xpos2 and yint1 == self.ypos1 and yint2 == self.ypos2:
                del main_canvas.int_list[z]
                
            elif xint2 == self.xpos1 and xint1 == self.xpos2 and yint2 == self.ypos1 and yint1 == self.ypos2:
                del main_canvas.int_list[z]
                
        #Help to remove one locking value on spin object. If lock_status = 0 after this, the spin is officially
        #unlocked.
        for j in main_canvas.spin_list:
            spinx, spiny = main_canvas.coords(j.spin)
            if spinx == self.xpos1 and spiny == self.ypos1:
                j.lock_status -= 1
            
            if spinx == self.xpos2 and spiny == self.ypos2:
                j.lock_status -= 1
                
                
    def resume(self):
        self.del_query.destroy()
        
    def Error_Close_Msg(self):
        self.error_win = tk.Toplevel()
        
        self.error_msg = tk.Label(self.error_win, text = 
                                  'Error! Please place spins at least one space apart!')
        self.error_msg.grid(row = 1, column = 0)

        ok_button = tk.Button(self.error_win, text = 'Ok', command = self.delete_err)
        ok_button.grid(row = 2, column = 0)
        
    def delete_err(self):
        self.error_win.destroy()

class Main_Screen(tk.Frame):

    def __init__(self, master):
        
        tk.Frame.__init__(self, master)
        
        #Create main canvas on application page.
        global main_canvas        
        main_canvas = tk.Canvas(self, width = canvas_width, height = canvas_height, bg = 'white')
       
        #Canvas position.
        main_canvas.grid(column = 0, row = 0)
        
        main_canvas.grid_xlines = []
        main_canvas.grid_ylines = []
        x_end = x_start + dx_grid * x_number
        y_end = y_start + dy_grid * y_number
        
        #Store grid information onto main canvas and create the grid.
        for i in range(x_number + 1):
            val = i * dx_grid + x_start
            main_canvas.grid_xlines.append(val)
            main_canvas.create_line(val, y_start, val, y_end, fill = 'grey')
            
        for j in range(y_number + 1):
            val = j * dy_grid + y_start
            main_canvas.grid_ylines.append(val)
            main_canvas.create_line(x_start, val, x_end, val, fill = 'grey')
        
        #Initialise the spin count variable.
        main_canvas.spin_count = 0
        
        #Creates spin 1 as the first element of the list.
        main_canvas.spin_list = [Spin_Object(
            spin_type, spin_posx_init, spin_posy_init)] 

        #Create button widget for mode change.
        main_canvas.mode_button = tk.Button(
            self, text = 'Interaction', command = self.mode_to_int)
        main_canvas.mode_window = main_canvas.create_window(
            900, 300, window = main_canvas.mode_button)
        
        #Initialise interaction matrix.
        main_canvas.int_list = []
        
        #Button to click for calculations.
        main_canvas.calc_button = tk.Button(
            self, text = 'Tabulate', command = self.calc_initiate)
        main_canvas.calc_window = main_canvas.create_window(
            900, 350, window = main_canvas.calc_button)
        
    def mode_to_int(self):
        #Change button to "pressed down" mode.
        main_canvas.mode_button.configure(relief = 'sunken', command = self.mode_to_spin)
        main_canvas.itemconfigure(main_canvas.mode_window, window = main_canvas.mode_button)
        
        for i in main_canvas.int_list:
            main_canvas.tag_bind(i.arrow, '<Button-1>', i.delete_popup)
        
        #Create variable link status to track clicks on spin buttons.
        main_canvas.link_status = -1
        
        #Initialise variables.
        main_canvas.s_button_list = []
        
        for i in main_canvas.spin_list:
            x_pos, y_pos = main_canvas.coords(i.spin)
            
            #Check that the spin we are looking at is not at its original position (outside grid).
            if x_pos != i.xpos:
                main_canvas.s_button_list.append(
                    Spin_Button(spin_type, x_pos, y_pos, i.spin_number))
                
    def mode_to_spin(self):
        #Raise button.
        main_canvas.mode_button.configure(relief = 'raised', command = self.mode_to_int)
        main_canvas.itemconfigure(main_canvas.mode_window, window = main_canvas.mode_button)
        
        main_canvas.s_button_list = []
        main_canvas.delete('sp_button')
        
        for i in main_canvas.int_list:
            main_canvas.tag_unbind(i.arrow, '<Button-1>')
            
    def calc_initiate(self):
        #To start calculations, need to extract all spins & interaction info.
        
        main_canvas.spin_info = np.zeros((len(main_canvas.spin_list)-1,3))
        z = int(0)
        
        #Extract xpos & ypos info for spin.
        for i in main_canvas.spin_list:
            
            xpos, ypos = main_canvas.coords(i.spin)
            
            #Ignore spin that is at original position.
            if xpos != spin_posx_init or ypos != spin_posy_init:
                main_canvas.spin_info[z] = [z, xpos, ypos]
                z += 1
            
        z = 0
        main_canvas.int_info = np.zeros((len(main_canvas.int_list),3))
        
        #Extract spin numbers the interaction is linking.
        for i in main_canvas.int_list:
            for j in range(len(main_canvas.spin_info)):
                if (i.xpos1 == main_canvas.spin_info[j][1]) and (i.ypos1 == main_canvas.spin_info[j][2]):
                    spin1 = main_canvas.spin_info[j][0]
                if (i.xpos2 == main_canvas.spin_info[j][1]) and (i.ypos2 == main_canvas.spin_info[j][2]):
                    spin2 = main_canvas.spin_info[j][0]
            if spin1 > spin2:
                temp = spin2
                spin2 = spin1
                spin1 = temp        
            main_canvas.int_info[z] = [z,spin1,spin2]
            z += 1
            
        #Initialising matrix.
        D = spa.bsr_matrix(np.zeros((2**len(main_canvas.spin_info),2**len(main_canvas.spin_info))))
        
        #Extract spins corresponding to each interaction arrow. Then create and interaction term and add it to 
        #the Hamiltoninan (D).
        for i in range(len(main_canvas.int_info)):
            spin1 = int(main_canvas.int_info[i][1])
            spin2 = int(main_canvas.int_info[i][2])            
            Int = Create_Int(spin1, spin2, len(main_canvas.spin_info))
            D = D + J * Int
        
        #If there is only two spins, use eig to solve for eigenvalues.
        if len(main_canvas.spin_info) == 2:
            D = D.todense()
            val, vec = np.linalg.eig(D)
            
        #Else, use eigsh.
        else:
            val, vec = eigsh(D, k = 6, which = 'SA')
        
        #Sorts the eigenvalues & eigenvectors.
        ind = np.argsort(val)
        val = np.real(val[ind].round(decimals = 2))
        vec = vec[:,ind]
        
        
        #Create the result window that outputs the lowest 4 energy values.
        self.result_window = tk.Toplevel()
        self.result = tk.Label(self.result_window, 
                               text = 'E1 = {0}\nE2 = {1}\nE3 = {2}\nE4 = {3}'.format(val[0], val[1], val[2], val[3]))
        self.result.grid(row = 0, column = 0)


if __name__ == '__main__':
    app = tk.Tk()
    Main_Screen(app).pack()
    app.mainloop()
