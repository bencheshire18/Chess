import pygame
import os
import time

# Initialize Pygame
pygame.init()

# Set the initial dimensions of the window
window_width = 800
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
    def __init__(self, x, y, colour, size):
        self.x = x
        self.y = y
        self.size = size
        self.colour = colour

    def draw(self):
        pygame.draw.rect(window, self.colour, (self.x, self.y, self.size + 1, self.size + 1))

def read_fen_position(fen_filepath):
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the path to the other file
    file_path = os.path.join(script_dir, 'Positions', fen_filepath)

    # Open and read the file
    with open(file_path, 'r') as file:
        fen = file.read()

    params = fen.split(' ')
    fen = params[0]
    active_colour = params[1]
    castling = params[2]
    en_passant = params[3]
    halfmove = params[4]
    fullmove = params[5]

    ranks = fen.split('/')
    position = []
    for rank in ranks:
        for char in rank:
            if char.isdigit():
                for i in range(int(char)):
                    position.append(None)
            else:
                position.append(char)
    return position, active_colour, castling, en_passant, halfmove, fullmove

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
                piece_image = pygame.transform.scale(piece_image, (int(square_size), int(square_size)))
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

# Read the FEN position
position, active_colour, castling, en_passant, halfmove, fullmove = read_fen_position('2.0_Position_fen.txt')

def draw_game():
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

    if castling != '-':
        if 'K' in castling:
            text = font.render("Kingside Castling available", True, WHITE)
            text_rect = text.get_rect()
            text_rect.center = (window_width * (7/8), 100)
            window.blit(text, text_rect)
        if 'k' in castling:
            text = font.render("Queenside Castling available", True, WHITE)
            text_rect = text.get_rect()
            text_rect.center = (window_width * (7/8), 150)
            window.blit(text, text_rect)
        if 'Q' in castling:
            text = font.render("Kingside Castling available", True, WHITE)
            text_rect = text.get_rect()
            text_rect.center = (window_width * (7/8), 200)
            window.blit(text, text_rect)
        if 'q' in castling:
            text = font.render("Queenside Castling available", True, WHITE)
            text_rect = text.get_rect()
            text_rect.center = (window_width * (7/8), 250)
            window.blit(text, text_rect)
    elif castling == '-':
        text = font.render("No Castling available", True, WHITE)
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

def check_valid_moves(piece, position, square):
    valid_moves = []

    def within_bounds(new_square):
        return 0 <= new_square < 64
    
    if piece == 'p':
        if position[square + 8] is None:
            valid_moves.append(square + 8)
            if square < 16 and position[square + 16] is None:
                valid_moves.append(square + 16)
        if square % 8 != 0 and position[square + 7] is not None and position[square + 7].isupper():
            valid_moves.append(square + 7)
        if square % 8 != 7 and position[square + 9] is not None and position[square + 9].isupper():
            valid_moves.append(square + 9)
    
    if piece == 'P':
        if position[square - 8] is None:
            valid_moves.append(square - 8)
            if square > 47 and position[square - 16] is None:
                valid_moves.append(square - 16)
        if square % 8 != 0 and position[square - 9] is not None and position[square - 9].islower():
            valid_moves.append(square - 9)
        if square % 8 != 7 and position[square - 7] is not None and position[square - 7].islower():
            valid_moves.append(square - 7)

    if piece == 'Q' or piece == 'q' or piece == 'R' or piece == 'r':
        # Vertical and horizontal moves for rooks and queens
        for i in range(1, 8):
            new_square = square + i * 8
            if within_bounds(new_square):
                if position[new_square] is None:
                    valid_moves.append(new_square)
                else:
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
                    valid_moves.append(new_square)
                    break
            else:
                break
        for i in range(1, 8):
            new_square = square + i
            if within_bounds(new_square) and new_square // 8 == square // 8:
                if position[new_square] is None:
                    valid_moves.append(new_square)
                else:
                    valid_moves.append(new_square)
                    break
            else:
                break
        for i in range(1, 8):
            new_square = square - i
            if within_bounds(new_square) and new_square // 8 == square // 8:
                if position[new_square] is None:
                    valid_moves.append(new_square)
                else:
                    valid_moves.append(new_square)
                    break
            else:
                break

    if piece == 'Q' or piece == 'q' or piece == 'B' or piece == 'b':
        # Diagonal moves for bishops and queens
        for i in range(1, 8):
            new_square = square + i * 7
            if within_bounds(new_square) and abs(new_square % 8 - square % 8) == i:
                if position[new_square] is None:
                    valid_moves.append(new_square)
                else:
                    valid_moves.append(new_square)
                    break
            else:
                break
        for i in range(1, 8):
            new_square = square + i * 9
            if within_bounds(new_square) and abs(new_square % 8 - square % 8) == i:
                if position[new_square] is None:
                    valid_moves.append(new_square)
                else:
                    valid_moves.append(new_square)
                    break
            else:
                break
        for i in range(1, 8):
            new_square = square - i * 7
            if within_bounds(new_square) and abs(new_square % 8 - square % 8) == i:
                if position[new_square] is None:
                    valid_moves.append(new_square)
                else:
                    valid_moves.append(new_square)
                    break
            else:
                break
        for i in range(1, 8):
            new_square = square - i * 9
            if within_bounds(new_square) and abs(new_square % 8 - square % 8) == i:
                if position[new_square] is None:
                    valid_moves.append(new_square)
                else:
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
            (square + 6, file < 7 and rank < 7),
            (square - 6, file > 0 and rank > 0),
            (square - 10, file > 1 and rank > 0),
            (square - 15, file > 0 and rank > 1),
            (square - 17, file < 7 and rank > 1)            
        ]

        for move, condition in knight_moves:
            if within_bounds(move) and condition:
                valid_moves.append(move)

    if piece == 'K' or piece == 'k':
        king_moves = [
            square + 8, square + 9, square + 1, square - 7,
            square - 8, square - 9, square - 1, square + 7
        ]
        for move in king_moves:
            if within_bounds(move):
                valid_moves.append(move)

    return valid_moves

def draw_valid_moves(valid_moves, board_x, board_y, square_size):
    for move in valid_moves:
        i = move // 8
        j = move % 8
        x = board_x + j * square_size + square_size / 2
        y = board_y + i * square_size + square_size / 2
        pygame.draw.circle(window, GREY, (int(x), int(y)), int(square_size / 4), 50)

def main():
    global window, window_width, window_height  # Declare window, window_width, and window_height as global variables
    running = True
    piece_selected = False

    # Mouse button state and debounce time
    mouse_button_held = False
    debounce_time = 0.2  # 200 milliseconds debounce time
    last_click_time = 0

    draw_game()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                window_width, window_height = event.w, event.h
                window = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
                draw_game()

        # Get the mouse position
        x, y = pygame.mouse.get_pos()

        # Calculate the board size and position
        board_size = min(window_width, window_height) * 0.8  # Board takes 80% of the smaller dimension
        board_x = 25 + window_width * 0.1
        board_y = (window_height / 2 - board_size / 2)

        square_size = board_size / 8
        i = int((y - board_y) // square_size)
        j = int((x - board_x) // square_size)
        if 0 <= i < 8 and 0 <= j < 8:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    current_time = time.time()
                    if not mouse_button_held and (current_time - last_click_time > debounce_time):
                        mouse_button_held = True
                        last_click_time = current_time
                        draw_board(board_x, board_y, board_size)
                        pygame.draw.rect(window, (219, 194, 70, 50), (board_x + j * square_size, board_y + i * square_size, square_size + 1, square_size + 1))
                        draw_pieces(position, board_x, board_y, board_size)
                        if position[i * 8 + j] is not None:
                            draw_valid_moves(check_valid_moves(position[i * 8 + j], position, i * 8 + j), board_x, board_y, square_size)
                        piece_selected = True
            
            # Highlight the current piece and valid moves
            if event.type == pygame.MOUSEBUTTONDOWN and piece_selected is True:
                if event.button == 3:
                    current_time = time.time()
                    if not mouse_button_held and (current_time - last_click_time > debounce_time):
                        mouse_button_held = True
                        last_click_time = current_time
                        draw_board(board_x, board_y, board_size)
                        draw_pieces(position, board_x, board_y, board_size)
                        piece_selected = False

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