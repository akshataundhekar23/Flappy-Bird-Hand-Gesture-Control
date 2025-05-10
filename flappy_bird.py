import pygame
import random
import cv2
import mediapipe as mp
import numpy as np
import sys

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.2
FLAP_STRENGTH = -6
PIPE_SPEED = 3
PIPE_SPAWN_TIME = 1500
PIPE_GAP = 350
FLAP_COOLDOWN = 500

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Load background and bird image
background_image = pygame.image.load("Forest.jpg")
background_image = pygame.transform.scale(background_image, (background_image.get_width(), SCREEN_HEIGHT))
bird_image = pygame.image.load("bird.png")
bird_image = pygame.transform.scale(bird_image, (50, 35))  # Adjust bird size

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird - Hand Controlled")
clock = pygame.time.Clock()

# Background scroll setup
background_scroll = 0
background_speed = 1

def draw_scrolling_background():
    global background_scroll
    bg_width = background_image.get_width()
    background_scroll -= background_speed
    if background_scroll <= -bg_width:
        background_scroll = 0
    screen.blit(background_image, (background_scroll, 0))
    screen.blit(background_image, (background_scroll + bg_width, 0))

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Open camera
cap = cv2.VideoCapture(0)

# Font
font = pygame.font.Font(None, 36)

class Bird:
    def __init__(self):
        self.x = SCREEN_WIDTH // 3
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.size = 30  # Used for logic, image will be rendered separately

    def move(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def draw(self):
        screen.blit(bird_image, (self.x - 25, self.y - 17))  # Center bird image (50x35)

    def check_collision(self, pipes):
        bird_rect = pygame.Rect(self.x - 25, self.y - 17, 50, 35)
        if self.y <= 0 or self.y >= SCREEN_HEIGHT:
            return True
        for pipe in pipes:
            if bird_rect.colliderect(pipe.top_rect) or bird_rect.colliderect(pipe.bottom_rect):
                return True
        return False

class Pipe:
    def __init__(self):
        self.gap_y = random.randint(200, SCREEN_HEIGHT - 200)
        self.x = SCREEN_WIDTH
        self.width = 70
        self.scored = False
        self.top_height = self.gap_y - PIPE_GAP // 2
        self.bottom_height = SCREEN_HEIGHT - (self.gap_y + PIPE_GAP // 2)
        self.top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        self.bottom_rect = pygame.Rect(self.x, SCREEN_HEIGHT - self.bottom_height, self.width, self.bottom_height)

    def move(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self):
        pygame.draw.rect(screen, GREEN, self.top_rect)
        pygame.draw.rect(screen, GREEN, self.bottom_rect)

def process_hand_gesture(frame, ref_line_px=200):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    should_flap = False

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            h, w, _ = frame.shape
            index_y_px = int(index_tip.y * h)

            if index_y_px < ref_line_px:
                should_flap = True

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Draw reference line
    cv2.line(frame, (0, ref_line_px), (frame.shape[1], ref_line_px), (0, 255, 0), 2)
    return should_flap, frame

def show_text(text, y_offset=0):
    rendered_text = font.render(text, True, WHITE)
    text_rect = rendered_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    screen.blit(rendered_text, text_rect)

def start_screen():
    while True:
        draw_scrolling_background()
        show_text("Flappy Bird - Hand Controlled")
        show_text("Raise finger above line to flap", 40)
        show_text("Press SPACE or raise hand to start", 80)
        pygame.display.flip()

        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        should_flap, processed_frame = process_hand_gesture(frame)
        cv2.imshow("Hand Tracking", processed_frame)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                cv2.destroyAllWindows()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return
        if should_flap:
            return

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            pygame.quit()
            sys.exit()

def game_over_screen(score):
    while True:
        draw_scrolling_background()
        show_text(f"Game Over! Score: {score}")
        show_text("Press R to Restart or Q to Quit", 40)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                cv2.destroyAllWindows()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                elif event.key == pygame.K_q:
                    cap.release()
                    cv2.destroyAllWindows()
                    pygame.quit()
                    sys.exit()

def main():
    global background_scroll
    while True:
        start_screen()
        bird = Bird()
        pipes = []
        score = 0
        last_pipe = pygame.time.get_ticks()
        last_flap_time = 0
        running = True
        background_scroll = 0

        while running:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            should_flap, processed_frame = process_hand_gesture(frame)

            current_time = pygame.time.get_ticks()
            if should_flap and current_time - last_flap_time > FLAP_COOLDOWN:
                bird.flap()
                last_flap_time = current_time

            cv2.imshow("Hand Tracking", processed_frame)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    cap.release()
                    cv2.destroyAllWindows()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    bird.flap()

            now = pygame.time.get_ticks()
            if now - last_pipe > PIPE_SPAWN_TIME:
                pipes.append(Pipe())
                last_pipe = now

            bird.move()
            for pipe in pipes:
                pipe.move()
                if not pipe.scored and pipe.x < bird.x:
                    score += 1
                    pipe.scored = True

            pipes = [pipe for pipe in pipes if pipe.x > -pipe.width]

            if bird.check_collision(pipes):
                break

            draw_scrolling_background()
            bird.draw()
            for pipe in pipes:
                pipe.draw()

            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))

            pygame.display.flip()
            clock.tick(60)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                running = False
                break

        if not game_over_screen(score):
            break

if __name__ == "__main__":
    main()
