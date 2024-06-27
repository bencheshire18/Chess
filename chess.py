import pygame
import os
import time
import sys

# Initialize Pygame
pygame.init()

# Set the initial dimensions of the window
window_width = 1200
window_height = 600
window_size = (window_width, window_height)

# Create the Pygame window
window = pygame.display.set_mode(window_size, pygame.RESIZABLE)
pygame.display.set_caption("Chess Game")

# Set the colours
BOARD_WHITE = (237, 214, 176)
BOARD_BLACK = (184, 135, 98 )
BACKGROUND  = (48 , 46 , 43 )
BLACK       = (0  , 0  , 0  )
WHITE       = (255, 255, 255)
GREY        = (128, 128, 128)

# Set the font
font = pygame.font.Font(None, 20)

# Set the clock
clock = pygame.time.Clock()

class Square:
    def __init__(self, x, y, colour, size, en_passant=False):
        self.x = x
        self.y = y
        self.size = size
        self.colour = colour
        self.en_passant = en_passant

    def draw(self):
        pygame.draw.rect(window, self.colour, (self.x, self.y, self.size + 1, self.size + 1))

def read_fen_position(fen_input):
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the path to the other file
    file_path = os.path.join(script_dir, 'Positions', fen_input)

    # Check if the input is a file path or a plain FEN string
    if os.path.isfile(file_path):
        # print(f"**Debug**\tDetected as filepath: {file_path}")
        # It's a file path, read the FEN string from the file
        try:
            with open(file_path, 'r') as file:
                fen_text = file.read()
                # print(f"**Debug**\tFEN Text: {fen_text}")
                fen = fen_text.strip()
                # print(f"**Debug**\tStripped data: {fen}")
        except Exception as e:
            # print(f"**Error**\tUnable to read file: {fen_input}\n{e}")
            return None
    else:
        # print(f"**Debug**\tDetected as FEN string: {fen_input}")
        # It's a plain FEN string
        fen_text = fen_input
        fen = fen_input.strip()

    # Split the FEN string into its components
    # print(f"**Debug**\tFEN data: {fen}")
    params = fen.split(' ')
    if len(params) < 6:
        print(f"**Error**\tInvalid FEN String: {fen}")
        return None
    # print(f"**Debug**\tPost splitting params\tparams: {params}")
    fen = params[0]
    active_colour = params[1]
    castling_availability = []
    for char in params[2]:
        castling_availability.append(char)
    en_passant = params[3]
    halfmove = int(params[4])
    fullmove = int(params[5])

    # Process the board position part of the FEN string
    ranks = fen.split('/')
    position = []
    for rank in ranks:
        for char in rank:
            if char.isdigit():
                for i in range(int(char)):
                    position.append(None)
            else:
                position.append(char)

    return position, active_colour, castling_availability, en_passant, halfmove, fullmove, fen_text

def write_fen_position(position, active_colour, castling_availability, en_passant_target, halfmove, fullmove):
    current_fen = ''
    index = 0
    is_none = False
    counter = 0
    
    for square in position:
        # Write out the position
        if index % 8 == 0 and index != 0:
            if is_none == True:
                current_fen += str(counter)
                counter = 0
            current_fen += '/'
        if square is not None:
            if is_none == True:
                if counter != 0:
                    current_fen += str(counter)
                is_none = False
            current_fen += square
        if square == None:
            if is_none == False:
                is_none = True
                counter = 0
            if is_none == True:
                counter += 1
        index += 1

    if is_none:
        current_fen += str(counter)

    current_fen += ' '

    # Add active colour
    current_fen += active_colour

    current_fen += ' '
    
    castling_list = []

    # Add the castling_availability availability
    if castling_availability == '-':
        castling_list = ['-']
    if 'K' in castling_availability:
        castling_list.append('K')
    if 'k' in castling_availability:
        castling_list.append('k')
    if 'Q' in castling_availability:
        castling_list.append('Q')
    if 'q' in castling_availability:
        castling_list.append('q')

    desired_order = ['K', 'Q', 'k', 'q']
    order_dict = {char: index for index, char in enumerate(desired_order)}
    castling_list = sorted(set(castling_availability), key=lambda char: order_dict[char] if char in order_dict else len(desired_order))

    if castling_list:
        for item in castling_list:
            current_fen += str(item)
    else:
        current_fen += '-'

    current_fen += ' '

    # Add the en passant target square
    current_fen += en_passant_target

    current_fen += ' '

    # Add halfmove clock
    current_fen += str(halfmove)

    current_fen += ' '

    # Add fullmove number
    current_fen += str(fullmove)

    return current_fen

def draw_board(board_x, board_y, board_size):
    # Draw the squares
    square_size = board_size / 8
    for i in range(8):
        for j in range(8):
            if (i + j) % 2 == 0:
                colour = BOARD_WHITE
            else:
                colour = BOARD_BLACK
            square = Square(board_x + j * square_size, board_y + i * square_size, colour, square_size)
            square.draw()

def draw_pieces(position, board_x, board_y, board_size):
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the path to the other file
    file_path = os.path.join(script_dir, 'Piece_Sprites/')

    piece_dict = {
        'r': file_path + 'bR.png',
        'n': file_path + 'bN.png',
        'b': file_path + 'bB.png',
        'q': file_path + 'bQ.png',
        'k': file_path + 'bK.png',
        'p': file_path + 'bP.png',
        'R': file_path + 'wR.png',
        'N': file_path + 'wN.png',
        'B': file_path + 'wB.png',
        'Q': file_path + 'wQ.png',
        'K': file_path + 'wK.png',
        'P': file_path + 'wP.png'
    }
    # Draw the pieces
    square_size = board_size / 8
    for i in range(8):
        for j in range(8):
            piece = position[i * 8 + j]
            if piece is not None:
                piece_image = pygame.image.load(piece_dict[piece])
                piece_image = pygame.transform.smoothscale(piece_image, (int(square_size), int(square_size)))
                window.blit(piece_image, (board_x + j * square_size, board_y + i * square_size))
            else:
                text = font.render("None", True, WHITE)
                text_rect = text.get_rect(center=(board_x + j * square_size + square_size / 2, board_y + i * square_size + square_size / 2))
                window.blit(text, text_rect)
            text = font.render(str(i * 8 + j), True, WHITE)
            text_rect = text.get_rect(center=(board_x + j * square_size + 7, board_y + i * square_size + 7))
            window.blit(text, text_rect)          

def recognise_clicked_piece(x, y, board_x, board_y, board_size):
    square_size = board_size / 8
    i = int((y - board_y) // square_size)
    j = int((x - board_x) // square_size)
    return i * 8 + j

def draw_game(position, active_colour, castling_availability, en_passant, halfmove, fullmove):
    # Clear the screen
    window.fill(BACKGROUND)

    # Calculate the board size and position
    board_size = min(window_width, window_height) * 0.8  # Board takes 80% of the smaller dimension
    board_x = 25 + window_width * 0.1
    board_y = (window_height / 2 - board_size / 2)

    # Draw the board and pieces
    draw_board(board_x, board_y, board_size)
    draw_pieces(position, board_x, board_y, board_size)

    # Draw the rank and file labels
    square_size = board_size / 8
    for i in range(8):
        text = font.render(str(8 - i), True, WHITE)
        text_rect = text.get_rect(center=(board_x - 20, board_y + i * square_size + square_size / 2))
        window.blit(text, text_rect)
        text = font.render(chr(97 + i), True, WHITE)
        text_rect = text.get_rect(center=(board_x + i * square_size + square_size / 2, board_y + board_size + 20))
        window.blit(text, text_rect)

    # Render text to the right hand side of the screen
    if active_colour == 'w':
        text = font.render("White to move", True, WHITE)
        text_rect = text.get_rect()
        text_rect.center = (window_width * (7/8), 50)
        window.blit(text, text_rect)
    elif active_colour == 'b':
        text = font.render("Black to move", True, WHITE)
        text_rect = text.get_rect()
        text_rect.center = (window_width * (7/8), 50)
        window.blit(text, text_rect)

    if castling_availability != '-':
        if 'K' in castling_availability:
            text = font.render("Kingside castling_availability available", True, WHITE)
            text_rect = text.get_rect()
            text_rect.center = (window_width * (7/8), 100)
            window.blit(text, text_rect)
        if 'k' in castling_availability:
            text = font.render("Queenside castling_availability available", True, WHITE)
            text_rect = text.get_rect()
            text_rect.center = (window_width * (7/8), 150)
            window.blit(text, text_rect)
        if 'Q' in castling_availability:
            text = font.render("Kingside castling_availability available", True, WHITE)
            text_rect = text.get_rect()
            text_rect.center = (window_width * (7/8), 200)
            window.blit(text, text_rect)
        if 'q' in castling_availability:
            text = font.render("Queenside castling_availability available", True, WHITE)
            text_rect = text.get_rect()
            text_rect.center = (window_width * (7/8), 250)
            window.blit(text, text_rect)
    elif castling_availability == '-':
        text = font.render("No castling_availability available", True, WHITE)
        text_rect = text.get_rect()
        text_rect.center = (window_width * (7/8), 100)
        window.blit(text, text_rect)

    if en_passant != '-':
        text = font.render(f"En passant square: {en_passant}", True, WHITE)
        text_rect = text.get_rect()
        text_rect.center = (window_width * (7/8), 300)
        window.blit(text, text_rect)
    elif en_passant == '-':
        text = font.render("No en passant square", True, WHITE)
        text_rect = text.get_rect()
        text_rect.center = (window_width * (7/8), 300)
        window.blit(text, text_rect)

    text = font.render(f"Halfmove: {halfmove}", True, WHITE)
    text_rect = text.get_rect()
    text_rect.center = (window_width * (7/8), 350)
    window.blit(text, text_rect)

    text = font.render(f"Fullmove: {fullmove}", True, WHITE)
    text_rect = text.get_rect()
    text_rect.center = (window_width * (7/8), 400)
    window.blit(text, text_rect)

def check_valid_moves(piece, position, square, en_passant_index, castling_availability, active_colour, check=False):

    if piece is not None:
        if active_colour == 'w':
            if piece.islower():
                return [], False
        else:
            if piece.isupper():
                return [], False

    valid_moves = []

    def within_bounds(new_square):
        return 0 <= new_square < 64
    
    def is_opponent(piece, target):
        if target is None:
            return False
        if piece.islower() and target.isupper():
            return True
        if piece.isupper() and target.islower():
            return True
        return False

    if piece == 'p':
        if within_bounds(square + 8) and position[square + 8] is None:
            valid_moves.append(square + 8)
            if square < 16 and within_bounds(square + 16) and position[square + 16] is None:
                valid_moves.append(square + 16)
        if square % 8 != 0 and within_bounds(square + 7) and is_opponent(piece, position[square + 7]):
            valid_moves.append(square + 7)
        if  en_passant_index == square + 7 and square // 8 == 4:
            valid_moves.append(square + 7)
        if square % 8 != 7 and within_bounds(square + 9) and is_opponent(piece, position[square + 9]):
            valid_moves.append(square + 9)
        if en_passant_index == square + 9 and square // 8 == 4:
            valid_moves.append(square + 9)
    
    if piece == 'P':
        if within_bounds(square - 8) and position[square - 8] is None:
            valid_moves.append(square - 8)
            if square > 47 and within_bounds(square - 16) and position[square - 16] is None:
                valid_moves.append(square - 16)
        if square % 8 != 0 and within_bounds(square - 9) and is_opponent(piece, position[square - 9]):
            valid_moves.append(square - 9)
        if en_passant_index == square - 9 and square // 8 == 3:
            valid_moves.append(square - 9)
        if square % 8 != 7 and within_bounds(square - 7) and is_opponent(piece, position[square - 7]):
            valid_moves.append(square - 7)
        if en_passant_index == square - 7 and square // 8 == 3:
            valid_moves.append(square - 7)

    if piece == 'Q' or piece == 'q' or piece == 'R' or piece == 'r':
        # Vertical and horizontal moves for rooks and queens
        for i in range(1, 8):
            new_square = square + i * 8
            if within_bounds(new_square):
                if position[new_square] is None:
                    valid_moves.append(new_square)
                else:
                    if is_opponent(piece, position[new_square]):
                        valid_moves.append(new_square)
                    break
            else:
                break
        for i in range(1, 8):
            new_square = square - i * 8
            if within_bounds(new_square):
                if position[new_square] is None:
                    valid_moves.append(new_square)
                else:
                    if is_opponent(piece, position[new_square]):
                        valid_moves.append(new_square)
                    break
            else:
                break
        for i in range(1, 8):
            new_square = square + i
            if within_bounds(new_square) and square // 8 == new_square // 8:
                if position[new_square] is None:
                    valid_moves.append(new_square)
                else:
                    if is_opponent(piece, position[new_square]):
                        valid_moves.append(new_square)
                    break
            else:
                break
        for i in range(1, 8):
            new_square = square - i
            if within_bounds(new_square) and square // 8 == new_square // 8:
                if position[new_square] is None:
                    valid_moves.append(new_square)
                else:
                    if is_opponent(piece, position[new_square]):
                        valid_moves.append(new_square)
                    break
            else:
                break

    if piece == 'Q' or piece == 'q' or piece == 'B' or piece == 'b':
        # Diagonal moves for bishops and queens
        for i in range(1, 8):
            new_square = square + i * 7
            if within_bounds(new_square) and new_square % 8 < square % 8:
                if position[new_square] is None:
                    valid_moves.append(new_square)
                else:
                    if is_opponent(piece, position[new_square]):
                        valid_moves.append(new_square)
                    break
            else:
                break
        for i in range(1, 8):
            new_square = square + i * 9
            if within_bounds(new_square) and new_square % 8 > square % 8:
                if position[new_square] is None:
                    valid_moves.append(new_square)
                else:
                    if is_opponent(piece, position[new_square]):
                        valid_moves.append(new_square)
                    break
            else:
                break
        for i in range(1, 8):
            new_square = square - i * 7
            if within_bounds(new_square) and new_square % 8 > square % 8:
                if position[new_square] is None:
                    valid_moves.append(new_square)
                else:
                    if is_opponent(piece, position[new_square]):
                        valid_moves.append(new_square)
                    break
            else:
                break
        for i in range(1, 8):
            new_square = square - i * 9
            if within_bounds(new_square) and new_square % 8 < square % 8:
                if position[new_square] is None:
                    valid_moves.append(new_square)
                else:
                    if is_opponent(piece, position[new_square]):
                        valid_moves.append(new_square)
                    break
            else:
                break

    if piece == 'N' or piece == 'n':
        file = square % 8
        rank = square // 8

        knight_moves = [
            (square + 17, file < 7 and rank < 6),
            (square + 15, file > 0 and rank < 6),
            (square + 10, file < 6 and rank < 7),
            (square + 6, file > 1 and rank < 7),
            (square - 6, file < 7 and rank > 0),
            (square - 10, file > 1 and rank > 0),
            (square - 15, file < 7 and rank > 1),
            (square - 17, file > 0 and rank > 1)
        ]

        for move, condition in knight_moves:
            if within_bounds(move) and condition:
                new_file = move % 8
                new_rank = move // 8
                if (position[move] is None or is_opponent(piece, position[move])) and abs(rank - new_rank) <= 2 and abs(file - new_file) <= 2:
                    valid_moves.append(move)

    if piece == 'K' or piece == 'k':
        king_moves = [
            square + 8, square + 9, square + 1, square - 7,
            square - 8, square - 9, square - 1, square + 7
        ]
        for move in king_moves:
            if within_bounds(move):
                if position[move] is None or is_opponent(piece, position[move]):
                    valid_moves.append(move)

        if piece.isupper():
            if 'K' in castling_availability:
                if position[61] is None and position[62] is None:
                    valid_moves.append(62)
            if 'Q' in castling_availability:
                if position[59] is None and position[58] is None and position[57] is None:
                    valid_moves.append(58)
        elif piece.islower():
            if 'k' in castling_availability:
                if position[5] is None and position[6] is None:
                    valid_moves.append(6)
            if 'q' in castling_availability:
                if position[1] is None and position[2] is None and position[3] is None:
                    valid_moves.append(2)

    return valid_moves

def promote_pawn(position, square, promotion_piece):
    position[square] = promotion_piece

def draw_valid_moves(valid_moves, board_x, board_y, square_size):
    for move in valid_moves:
        i = move // 8
        j = move % 8
        x = board_x + j * square_size + square_size / 2
        y = board_y + i * square_size + square_size / 2
        pygame.draw.circle(window, GREY, (int(x), int(y)), int(square_size / 4), 50)

def mouse_square_location(x, y, board_size, board_x, board_y):
    square_size = board_size / 8
    i = int((y - board_y) // square_size)
    j = int((x - board_x) // square_size)

    return i, j, square_size

def update_halfmove_clock(position, selected_square, halfmove_clock, was_capture):    
    """Updates the halfmove clock based on the current move."""

    try:
        piece = position[selected_square].lower()
    except AttributeError as e:
        sys.exit()

    if piece == 'p' or was_capture:
        halfmove_clock = 0
    else:
        halfmove_clock += 1

    # Check for 50-move rule draw (unchanged)
    if halfmove_clock >= 100:
        return halfmove_clock, True  # Game is a draw
    else:
        return halfmove_clock, False  # Game continues

def check_for_check(position):
    for square in position:
        if square is not None:
            valid_moves = check_valid_moves(position[square], position, square, en_passant_index=-1, castling_availability=[], active_colour='b')
            for move in valid_moves:
                if position[move].lower() == 'k':
                    return True
    
    return False

def main():

    castling_availability = ['K', 'Q', 'k', 'q']
    halfmove_toggle = True
    
    # Read the FEN position
    result = read_fen_position('6.0_Position_fen.txt')
    if result is None:
        print(f"Error reading FEN position.\tResult: {result}")
        sys.exit()
    else:
        position, active_colour, castling_availability, en_passant, halfmove, fullmove, fen_text = result
    
    print(f"active colour: {active_colour}")

    # map the grid notation to the board index
    grid_to_index = {
        'a8': 0, 'b8': 1, 'c8': 2, 'd8': 3, 'e8': 4, 'f8': 5, 'g8': 6, 'h8': 7,
        'a7': 8, 'b7': 9, 'c7': 10, 'd7': 11, 'e7': 12, 'f7': 13, 'g7': 14, 'h7': 15,
        'a6': 16, 'b6': 17, 'c6': 18, 'd6': 19, 'e6': 20, 'f6': 21, 'g6': 22, 'h6': 23,
        'a5': 24, 'b5': 25, 'c5': 26, 'd5': 27, 'e5': 28, 'f5': 29, 'g5': 30, 'h5': 31,
        'a4': 32, 'b4': 33, 'c4': 34, 'd4': 35, 'e4': 36, 'f4': 37, 'g4': 38, 'h4': 39,
        'a3': 40, 'b3': 41, 'c3': 42, 'd3': 43, 'e3': 44, 'f3': 45, 'g3': 46, 'h3': 47,
        'a2': 48, 'b2': 49, 'c2': 50, 'd2': 51, 'e2': 52, 'f2': 53, 'g2': 54, 'h2': 55,
        'a1': 56, 'b1': 57, 'c1': 58, 'd1': 59, 'e1': 60, 'f1': 61, 'g1': 62, 'h1': 63
    }

    index_to_grid = {v: k for k, v in grid_to_index.items()}

    if en_passant == '-':
        en_passant_index = -1
    else:
        en_passant_index = grid_to_index[en_passant]

    global window, window_width, window_height  # Declare window, window_width, and window_height as global variables
    running = True
    piece_selected = False

    # Mouse button state and debounce time
    mouse_button_held = False
    debounce_time = 0.1  # 100 milliseconds debounce time
    last_click_time = 0

    draw_game(position, active_colour, castling_availability, en_passant, halfmove, fullmove)

    while running:

        current_fen = write_fen_position(position, active_colour, castling_availability, en_passant, halfmove, fullmove)

        with open('./Positions/current_fen.txt', 'w') as file:
            file.write(current_fen)

        position, active_colour, castling_availability, en_passant, halfmove, fullmove, fen_text = read_fen_position(current_fen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                window_width, window_height = event.w, event.h
                window = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
                draw_game(position, active_colour, castling_availability, en_passant, halfmove, fullmove)

            # Get the mouse position
            x, y = pygame.mouse.get_pos()

            # Calculate the board size and position
            board_size = min(window_width, window_height) * 0.8  # Board takes 80% of the smaller dimension
            board_x = 25 + window_width * 0.1
            board_y = (window_height / 2 - board_size / 2)

            i, j, square_size = mouse_square_location(x, y, board_size, board_x, board_y)

            # If the mouse is within the grid
            if 0 <= i < 8 and 0 <= j < 8:
                check = check_for_check(position)
                # ** Selecting a square **
                # If the mouse is clicked and there is no piece selected 
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if piece_selected == False:
                        # left mouse button
                        if event.button == 1:
                            current_time = time.time()
                            # Debounce logic
                            if not mouse_button_held and (current_time - last_click_time > debounce_time):
                                selected_square = i * 8 + j
                                mouse_button_held = True
                                last_click_time = current_time
                                draw_board(board_x, board_y, board_size)
                                pygame.draw.rect(window, (219, 194, 70, 50), (board_x + j * square_size, board_y + i * square_size, square_size + 1, square_size + 1))
                                draw_pieces(position, board_x, board_y, board_size)
                                if position[selected_square] is not None:
                                    valid_moves = check_valid_moves(position[selected_square], position, selected_square, en_passant_index, castling_availability, active_colour)
                                    draw_valid_moves(valid_moves, board_x, board_y, square_size)
                                    piece_selected = True
                                else:
                                    piece_selected = False
                        
                    if piece_selected == True:
                        if event.button == 1:
                            # ** Move the piece via clicking **
                            current_time = time.time()

                            if not mouse_button_held and (current_time - last_click_time > debounce_time):
                                target_square = i * 8 + j
                                target_rank = target_square // 8
                                selected_rank = selected_square // 8
                                mouse_button_held = True
                                last_click_time = current_time
                                valid_moves = check_valid_moves(position[selected_square], position, selected_square, en_passant_index, castling_availability, active_colour)

                                if target_square in valid_moves:
                                    # White Kingside Castling
                                    if position[selected_square] == 'K' and target_square == 62:
                                        position[61] = position[63]
                                        position[63] = None
                                        castling_availability.remove('K')

                                    # Black Kingside Castling
                                    if position[selected_square] == 'k' and target_square == 6:
                                        position[5] = position[7]
                                        position[7] = None
                                        castling_availability.remove('k')
                                    
                                    # White Queenside Castling
                                    if position[selected_square] == 'K' and target_square == 58:
                                        position[59] = position[56]
                                        position[56] = None
                                        castling_availability.remove('Q')

                                    # Black Queenside Castling
                                    if position[selected_square] == 'k' and target_square == 2:
                                        position[3] = position[0]
                                        position[0] = None
                                        castling_availability.remove('q')
                                    
                                    # En Passant implementation
                                    if target_square == en_passant_index:
                                        if position[selected_square] == 'P':
                                            position[target_square + 8] = None
                                        if position[selected_square] == 'p':
                                            position[target_square - 8] = None
                                        was_capture = True
                                    
                                    # fullmove counter update
                                    if active_colour == 'w':
                                        fullmove += 1


                                    # Updating castling_availability
                                    if (selected_square == 63 or selected_square == 60) and 'K' in castling_availability:
                                        castling_availability.remove('K')
                                        
                                    elif (selected_square == 56 or selected_square == 60) and 'Q' in castling_availability:
                                        castling_availability.remove('Q')
                                        
                                    elif (selected_square == 7 or selected_square == 4) and 'k'  in castling_availability:
                                        castling_availability.remove('k')
                                        
                                    elif (selected_square == 0 or selected_square == 4) and 'q' in castling_availability:
                                        castling_availability.remove('q')
                                        
                                    # Updating En Passant square
                                    if selected_rank == 6 and target_rank == 4:
                                        en_passant_index = (target_rank + 1) * 8 + j
                                        en_passant_target = index_to_grid.get(en_passant_index)
                                    elif selected_rank == 1 and target_rank == 3:
                                        en_passant_index = (target_rank - 1) * 8 + j
                                        en_passant_target = index_to_grid.get(en_passant_index)
                                    else:
                                        en_passant_index = -1
                                        en_passant_target = '-'
                                        
                                    # print(f"**Debug**\twas_capture being determined\tposition[target_square]: {position[target_square]}")
                                    if position[target_square] is not None:
                                        was_capture = True
                                    else:
                                        was_capture = False
                                    position[target_square] = position[selected_square]
                                    position[selected_square] = None
                                    active_colour = 'b' if active_colour == 'w' else 'w'

                                    halfmove, is_draw = update_halfmove_clock(position, target_square, halfmove, was_capture)

                                    if target_square == en_passant_index:
                                        if target_rank == 2:
                                            position[target_square + 8] = None
                                        if target_rank == 5:
                                            position[target_square - 8] = None

                                else:
                                    draw_board(board_x, board_y, board_size)
                                    pygame.draw.rect(window, (219, 194, 70, 50), (board_x + j * square_size, board_y + i * square_size, square_size + 1, square_size + 1))
                                    draw_pieces(position, board_x, board_y, board_size)
                                    if target_square is not None:
                                        valid_moves = check_valid_moves(position[target_square], position, target_square, en_passant_index, castling_availability, active_colour)
                                        draw_valid_moves(valid_moves, board_x, board_y, square_size)
                                    if position[target_square] is not None:
                                        piece_selected = True
                                        selected_square = target_square
                                    else:
                                        piece_selected = False

                        if event.button == 3:
                            # ** Clear the selection **
                            current_time = time.time()
                            if not mouse_button_held and (current_time - last_click_time > debounce_time):
                                mouse_button_held = True
                                last_click_time = current_time
                                piece_selected = False
                                selected_square = -1
                                valid_moves = []
                                draw_game(position, active_colour, castling_availability, en_passant, halfmove, fullmove)
                                    

                if event.type == pygame.MOUSEBUTTONUP:
                    # ** Moving a piece via dragging **
                    target_square = i * 8 + j
                    # print(f"**Debug**\tevent.button: {event.button}\ttarget_square: {target_square}\tselected_square: {selected_square}")
                    if event.button == 1 and target_square != selected_square:
                        mouse_button_held = False
                        if piece_selected:
                            valid_moves = check_valid_moves(position[selected_square], position, selected_square, en_passant_index, castling_availability, active_colour)
                            if target_square in valid_moves:
                                
                                # White Kingside Castling
                                if position[selected_square] == 'K' and target_square == 62:
                                    position[61] = position[63]
                                    position[63] = None

                                # Black Kingside Castling
                                if position[selected_square] == 'k' and target_square == 6:
                                    position[5] = position[7]
                                    position[7] = None
                                
                                # White Queenside Castling
                                if position[selected_square] == 'K' and target_square == 58:
                                    position[59] = position[56]
                                    position[56] = None

                                # Black Queenside Castling
                                if position[selected_square] == 'k' and target_square == 2:
                                    position[3] = position[0]
                                    position[0] = None

                                # Move the piece
                                position[target_square] = position[selected_square]
                                position[selected_square] = None

                                draw_game(position, active_colour, castling_availability, en_passant, halfmove, fullmove)
                                piece_selected = False
                                active_colour = 'b' if active_colour == 'w' else 'w'
                            else:
                                piece_selected = False
                                draw_game(position, active_colour, castling_availability, en_passant, halfmove, fullmove)
                        else:
                            draw_game(position, active_colour, castling_availability, en_passant, halfmove, fullmove)

                        new_fen = write_fen_position(position, active_colour, castling_availability, en_passant_target, halfmove, fullmove)
                        print(f"New FEN: {new_fen}")

                # Check for mouse released event
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 or event.button == 3:
                        mouse_button_held = False
                    
        # Update the display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()