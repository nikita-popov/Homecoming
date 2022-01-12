from engine import *
pygame.init()

running = True
clock = pygame.time.Clock()
fps = 60

debug_hud = False
player = None
there = False
current_map = 1


def go_to_main_menu():
    for j in groups:
        j.empty()
    global new_game
    new_game = Button(100, 100, 400, 200, "yellow", 0, 20, "Новая игра", pygame.event.post, parameter=PLAYER_THERE)


if __name__ == "__main__":
    go_to_main_menu()
    while running:
        canvas.fill("white")
        clock.tick(fps)
        pygame.display.set_caption(f"{clock.get_fps()}")
        objects.update()
        objects.draw(canvas)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F5:
                    debug_hud = not debug_hud
            if event.type == pygame.USEREVENT:
                there = True
                player = open_map(f"map{current_map}.hcm")
                print("there")
            if event == NEXT_LEVEL:
                there = True
                current_map += 1
                player = open_map(f"map{current_map}.hcm")
                print("next")

        if there:
            if not player.alive:
                player = open_map(f"map{current_map}.hcm")
            if player.rect.x >= 600:
                for i in everything:
                    i.rect.x -= 5

            elif player.rect.x <= 400:
                for i in everything:
                    i.rect.x += 5

            if player.rect.y <= 200:
                for i in everything:
                    i.rect.y += 5

            elif player.rect.y >= 400:
                for i in everything:
                    i.rect.y -= 5
            if debug_hud:
                player.debug()
            player.draw_hud()
        pygame.display.flip()
pygame.quit()
