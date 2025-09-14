def getanim(s: str, frame: int) -> tuple[list[str], bool]:
    """
    Returns the animation s on frame frame
    :param s: animation path
    :param frame: frame to get
    :return: frame
    """
    with open(s, "r", encoding="utf-8") as f:
        frames = f.read().split("-FRAME-")
    f = False
    if frame >= len(frames) - 1:
        frame = len(frames) - 2
        f = True
    return frames[frame + 1].split("\n")[1:-2], f
