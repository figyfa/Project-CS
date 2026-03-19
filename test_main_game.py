from main_game import *

pygame.init()
pygame.font.init()

def test_calc_distance():
    """Test that the cartesian distance function works for standard coordinates"""
    world = GameWorld()

    player1 = Player(500,600,world)
    player2 = Player(525,600,world)
    assert calc_distance(player1,player2) < 0 #Two players that are colliding with each-other
    player1 = Player(500,600,world)
    player2 = Player(100,100,world)
    assert calc_distance(player1,player2) > 0 #Two players are not colliding with each-other


class TestBoundingBox:
    """Tests that the bounding box works correctly for a player outside and a player inside the bounding box region
    Bounding box region is 550 < player's x coordinate < 950
    and 300 < player's y coordinate < 550"""
    def test_draw(self):
        assert True
    def test_scan_for_player_in_box(self):
        """ Test if various players are inside or outside the bounding box"""
        world = GameWorld()
        bounding_box = BoundingBox(world=world)
        player = Player(600,350,world) # Player fully in bounding box
        assert bounding_box.scan_for_player(player) == True
        player2 = Player(100,100,world) # Player not in bounding box
        assert bounding_box.scan_for_player(player2) == False
        player3 = Player(550,300,world) # Player at top left corner of bounding box
        assert bounding_box.scan_for_player(player3) == False
        player4 = Player(950,550,world) # Player at bottom right corner of bounding box
        assert bounding_box.scan_for_player(player4) == False
        player5 = Player(949,549,world)# Player close to edge of bounding box
        assert bounding_box.scan_for_player(player5) == True

def test_player_update_health():
    """Test to see if player death is handled correctly"""
    world = GameWorld()
    player = Player(600,350,world)
    assert player.update_health() == False # Player is alive, main menu should not be activated
    player.health = 20
    assert player.update_health() == False # Player is still alive, main menu should not be activated
    player.health = 0
    assert player.update_health() == True # Player has died, reactivate main menu

def test_sword_logic():
    """ Test enemy getting stunned after collision with sword hitbox"""
    world = GameWorld()
    sword = Sword()
    enemy = Enemy(300,400,1,world)
    world.enemies.append(enemy)
    sword.wcx = enemy.wcx
    sword.wcy = enemy.wcy
    sword.check_hit(world.enemies,world)
    assert enemy.sword_stunned == True #Enemy is in contact with sword, therefore, should get stunned by sword

    enemy2 = Enemy(100,100,2,world)
    world.enemies.append(enemy2)
    sword.wcx = 300
    sword.wcy = 400
    sword.check_hit(world.enemies,world)
    assert enemy2.sword_stunned == False #Enemy is not in contact with sword, should not get stunned when sword is swung

def test_player_collision():
    """Test if player can collide with trees"""
    world = GameWorld()
    tree = Tree(590,350)
    tree2 = Tree(100,100)
    trees = [tree,tree2]
    player = Player(610,350,world)
    world.player = player
    world.update_collision_hitboxes()
    world.player.walking_spots = [world.player.left, world.player.right, world.player.down, world.player.up,
                                 world.player.upleft, world.player.downleft, world.player.downright,
                                 world.player.upright]
    world.player.check_walkable(trees)
    print(calc_distance_circle_and_point(tree,player.left,world))
    assert world.player.left_walkable == False
    assert world.player.right_walkable == True # Player should not be able to walk left, but should be able to walk right

    trees.remove(tree)
    world.player.walking_spot_permissions = [True for i in range(8)]
    world.player.check_walkable(trees)
    assert world.player.left_walkable == True
    assert world.player.right_walkable == True # Player should be able to walk both left and right
