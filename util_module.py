def center_text(screen, font, ypos, text, color, xRES):
    xdelta, ydelta = font.size(text)
    screen.blit(font.render(text, True, color), (xRES/2-xdelta/2, ypos-ydelta/2))