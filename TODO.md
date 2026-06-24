* Expand tileset generator to run at any res, including adding full-res source in place
* Make map movement less chunky
    * **JITTERY MAP MOVEMENT** Option 1 *sounds* like what we're looking for and seems like the most simple option. But, I'm not *sure*.
* Add Drops
    * Different glyphs for different weapon types, different colors for different materials.
* Add key for use item/pick up
* Add monsters and damage dealing
    * **LARGE MONSTER MECHANICS** *Option 2*
        * Multi-tile occupancy — The creature owns a N×N block of tiles. Movement, collision, and pathfinding all operate on the bounding box. Correct behavior, but touches is_walkable, _find_monster_next_step (BFS needs to check all leading edges), and the rendering loop. Most work, most correct.
    * Monster Spawning Mechanics
        * By level (random distribution)
        * Spawner-like (set frequency within biome, max spawns per map)
        * By chunk (spawn frequency per chunk, max spawns for chunk and for map)
    * Damage :
        Slash
            **Physical**
            Deals immediate damage. Inflicts Staggering.
            **Staggering** : (damage * stagger modifier)
        Blunt
            **Physical**
            Deals immediate damage. Inflicts Staggering.
            **Staggering** : (damage * stagger modifier)
        Pierce
            **Physical**
            Deals immediate damage. Inflicts Staggering.
            **Staggering** : (damage * stagger modifier)
        Fire
            **Elemental**
            Deals no immediate damage. Instead, spreads the damage over 5s (damage/5 per 1s). Taking subsequent Fire damage recalculates the tick damage and resets the duration. ((remaining tick damage + new damage)/5 = reevaluated tick damage (per 1s)).
            **Inflicted Effect** : Burning
                Duration : 5s
        Frost
            **Elemental**
            Deals immediate damage. Inflicts a slow effect, decreasing movement speed by % for 5s. Taking subsequent Frost damage resets the duration of the effect (but doesn't stack).
            **Inflicted Effect** : Frost
                Duration : 5s
        Lightning
            **Elemental**
            Deals immediate damage. Inflicts Electricity effect. Electricity is purely cosmetic. Inflicts Staggering.
            **Inflicted Effect** : Electricity
                Duration : 3s
            **Staggering** : (damage * stagger modifier)
        Poison
            **Elemental**
            Deals no immediate damage. Instead, spreads the damage over a duration (1+sqrt(3*damage)). Deals damage over time (damage/duration per 1s). Taking subsequent Poison damage resets the duration but does not stack.
            **Inflicted Effect** : Poison
                Duration : Varies
        Spirit
            **Elemental**
            Deals no immediate damage. Instead, spreads the damage over 3s (damage/6 per 0.5s). Taking subsequent Spirit damage recalculates the tick damage and resets the duration. ((remaining tick damage + new damage)/6 = reevaluated tick damage (per 0.5s)).
            **Inflicted Effect** : Spirit
                Duration : 3s
            **Damage Modifier Notes** : Players are Immune to Spirit damage.
        Chop
            **Terrain**
            Deals immediate damage. Only damages certain objects and a few creatures. Most creatures are immune to Chop damage.
            **Damage Modifier Notes** : Almost all creatures are immune to Chop damage.
        Pickaxe
            **Terrain**
            Deals immediate damage. Only damages certain objects and a few creatures. Most creatures are immune to Pickaxe damage.
            **Damage Modifier Notes** : Almost all creatures are immune to Pickaxe damage.
        Pure
            **Pure**
            Deals immediate damage. Pure damage ignores armor, blocking, and damage resistance. Specific items can reduce Pure damage from certain sources (lava, falling, etc.).
            **Damage Modifier Notes** : Nothing is resistant to Pure damage!
            **Damage Modifier Notes** : Some creatures can be resistant to certain sources of Pure damage.


* **Combat Mechancics : Spells/Powers/Abilities/Whatever**
    Fire
    Ice
    Electricity
    Force
    Psychic
    Earth
    Water
    Dark



* Monsters :
        * Meadows :
            * Greyling
            * Boar
            * Neck
            * Deer
            * ***Eikthyr***
        * Black Forest :
            * Greydwarf
            * Greydwarf Shaman
            * Greydwarf Brute
            * Skeleton
            * Rancid Remains
            * Troll
            * Bear
            * *Brenna*
            * ***The Elder***
        * Ocean :
            * *Serpent*
        * Swamp :
            * Draugr
            * Draugr Elite
            * Leech
            * Wraith
            * Abomination
            * Blob
            * Oozer
            * *Kvastur*
            * ***Bonemass***
        * Mountains :
            * Wolf
            * Drake
            * Ulv
            * Fenring
            * Cultist
            * Bat
            * Stone Golem
            * *Geirrhafa*
            * ***Moder***
        * Plains :
            * Fuling
            * Fuling Berserker
            * Fuling Shaman
            * Lox
            * Growth
            * Deathsquito
            * Vile
            * *Zil and Thungr*
            * ***Yagluth***
        * Mistlands :
            * Hare
            * Seeker
            * Seeker Soldier
            * Tick
            * Seeker Brood
            * Gjall
            * Dvergr Mage
            * Dvergr Rouge
            * ***The Queen***
        * Ashlands :
            * Bonemaw
            * Volture
            * Charred Twitcher
            * Charred Warrior
            * Charred Marksman
            * Charred Warlock
            * Asksvin
            * Lava Blob
            * Morgen
            * Fallen Valkyrie
            * *Lord Reto*
            * ***Fader***
* Add health bar
  * Add more weapons
      * Weapons as follows :
        * Meadows :
            * Wooden Sword                       Slash:5                      Use Stamina:3
            * Torch                              Blunt:4 Fire:15              Use Stamina:4
            * Club                               Blunt:12                     Use Stamina:4
            * Stone Axe                          Slash:15                     Use Stamina:6
            * Flint Axe                          Slash:20                     Use Stamina:6
            * Flint Knife                        Slash:6 Pierce:6  	          Use Stamina:3
            * Flint Spear                        Pierce:20			          Use Stamina:6
            * Crude Bow                          Pierce:22 				      Use Stamina:4/s
            * ***Antler Spear***                 Pierce:20 Pickaxe:10         Use Stamina:8
        * Black Forest :
            * Stagbreaker                        Blunt:20 Pierce:5            Use Stamina:20
            * Finewood Bow                       Pierce:32                    Use Stamina:6/s
            * Bronze Sword                       Slash:35				      Use Stamina:8
            * Bronze Axe                         Slash:40				      Use Stamina:8
            * Copper Knife                       Slash:12 Pierce:12           Use Stamina:5
            * Bronze Spear                       Pierce:35                    Use Stamina:8
            * Bronze Mace                        Blunt:35			          Use Stamina:8
            * Bronze Atgeir                      Pierce:45                    Use Stamina:8
            * Claws of the Bear                  Slash:25                     Use Stamina:6
            * **Rancid Mace**                    
            * **Troll Log**                      
            * **Surtling Bomb**                  
        * Ocean :
            * Abyssal Razor                     Slash:20 Pierce:20            Use Stamina:7
            * Abyssal Harpoon                   Pierce:10                     Use Stamina:10
        * Swamp :
            * Iron Sword                        Slash:55                      Use Stamina:10
            * Iron Mace                         Blunt:55                      Use Stamina:10
            * Ancient Bark Spear                Pierce:55                     Use Stamina:10
            * Iron Atgeir                       Pierce:65                     Use Stamina:10
            * Iron Knife                        Slash:20 Pierce:20            Use Stamina:7
            * Iron Axe                          Slash:60                      Use Stamina:10
            * Battleaxe                         Slash:70                      Use Stamina:15
            * Huntsman Bow                      Pierce:42                     Use Stamina:8/s
            * Iron Sledge                       Blunt:55                      Use Stamina:27
            * Ooze Bomb                         Poison:20                     Use Stamina:3
            * **Poison Dagger**                 
            * **Flail**                         
            * **Abomination Arm**               
            * ***Bonemass Blade***              
        * Mountains :
            * Silver Sword                      Slash:75 Spirit:30            Use Stamina:10
            * Silver Knife                      Slash:25 Pierce:25            Use Stamina:7
            * Frostner                          Blunt:35 Frost:40 Spirit:20   Use Stamina:10
            * Fang Spear                        Pierce:75                     Use Stamina:10
            * Crystal Battleaxe                 Slash:90 Spirit:30            Use Stamina:18
            * Flesh Rippers                     Slash:60                      Use Stamina:8
            * Draugr Fang                       Pierce:50 Poison:10           Use Stamina:10/s
            * **Stone Golem Arm**               
            * **Ice Bomb**                      
            * ***Moder Claw***                  
            * ***Frost Blade***                 
        * Plains :
            * Black Metal Sword                 Slash:95                      Use Stamina:12
            * Black Metal Atgeir                Pierce:105                    Use Stamina:12
            * Black Metal Axe                   Slash:100 	                  Use Stamina:12
            * Black Metal Knife                 Slash:30 Pierce:30            Use Stamina:8
            * Porcupine                         Blunt:40 Pierce:55	          Use Stamina:12
            * Vilebone Maulclaws                Slash:25 Pierce:50            Use Stamina:10
            * Black Metal Battleaxe             Slash:110                     Use Stamina:24
            * **Fuling Berserker Club**         Blunt:120                     Use Stamina:30
            * **Tar Sword**                     
            * **Tar Bomb**                      
            * ***Spirit Hammer***               
        * Mistlands :
            * Skol and Hati                     Slash:40 Pierce:40            Use Stamina:8
            * Krom                              Slash:150                     Use Stamina:20
            * Demolisher                        Blunt:145                     Use Stamina:35
            * Carapace Spear                    Pierce:115                    Use Stamina:14
            * Mistwalker                        Slash:75 Frost:40 Spirit:15   Use Stamina:14
            * Himminafl                         Pierce:80 Lightning:45        Use Stamina:14
            * Skull Splittur                    Slash:130                     Use Stamina:28
            * Arbalest                          Pierce:200                    Use Stamina:1/s
            * Spinesnap                         Pierce:72                     Use Stamina:14/s
            * Staff of Frost                    Frost:30                      Use Eitr:5
            * Staff of Embers                   Blunt:120 Fire:120            Use Eitr:35
            * Dead Raiser                       Summons Skellett              Use Eitr:100 Use Health:40%
            * Staff of Protection               Damage Absorption:200-700     Use Eitr:60 Use Health:40%
            * **Extractor Spear**               Pierce:95
            * **Staff of the Gjall**            
            * **Eitr Blade**                    
            * **Eitr Grenade**                  
            * **Staff of Eitr**                 
            * ***Staff of The Queen***          
            * ***Queen's Arm Greatsword***      Slash:200 Terrain:100        Use Stamina:
        * Ashlands :
            * Nidhogg                           Slash:135                    Use Stamina:14
            * Splitnir                          Pierce:135                   Use Stamina:14
            * Slayer                            Slash:170                    Use Stamina:24
            * Flametal Mace                     Blunt:135                    Use Stamina:14
            * Berserkir Axes                    Slash:140                    Use Stamina:14
            * Ash Fang                          Pierce:82                    Use Stamina:14/s
            * Ripper                            Pierce:220                   Use Stamina:1/s
            * Staff of Fracturing               Blunt:12 Fire:12             Use Eitr:24
            * Staff of Wilds                    Blunt:20 Poison:20           Use Eitr:50
            * Trollstav                         Fire:300 Blunt:100 Summon    Use Eitr:120 Use Health:60%
            * Dundr                             Lightning:18(total:216)      Use Eitr:28
            * **Celestial Staff**               
            * **Staff of Snapping Jaws**        
            * **Explosive Grenade**             
            * **Staff of Caltrops**             
            * **Lava Blade**                    
            * **Staff of the Charred**          
            * **Staff of Brimstone**            
            * ***Blade of Lord Reto***          
            * ***Fader Claw***                  
            * ***Staff of The Emerald Flame***  
* Add armor mechanic
* Add armor
    * Armor as follows :
        * Rag (Light)                                          Armor:1  Speed:+0%
        * Leather (Light)                                      Armor:2  Speed:+0%
        * Leather Cape                                         Armor:1  Speed:+0%
        * Troll Hide (Light, Sneak Bonus)                      Armor:6  Speed:+0%
        * Troll Hide Cape                                      Armor:2  Speed:+0%
        * Bronze (Heavy)                                       Armor:8  Speed:-5%
        * Root (Light, Damage res, Archery Bonus)              Armor:8  Speed:-2%
        * Iron (Heavy)                                         Armor:14 Speed:-5%
        * Fenris (Light, Dmg res, Speed Bonus)                 Armor:10 Speed:+3%
        * Fenris Cape (Speed Bonus)                            Armor:3  Speed:+5%
        * Wolf (Heavy)                                         Armor:20 Speed:-5%
        * Wolf Fur Cape (Frost Res)                            Armor:4  Speed:+0%
        * Vilebone (Light, Damage Bonus, Stamina Reduction)    Armor:12 Speed:+0%
        * Lox Hide Cape (Frost Res)                            Armor:5  Speed:+0%
        * Padded (Heavy)                                       Armor:26 Speed:-5%
        * Linen Cape                                           Armor:5  Speed:+0%
        * Eitrweave (Mage, Eitr Regen Bonus)                   Armor:16 Speed:-2%
        * Feather Cape (Frost Res, No Fall Damage)             Armor:6  Speed:+0%
        * Carapace (Heavy)                                     Armor:32 Speed:-5%
        * Embla (Mage, Eitr Regen Bonus)                       Armor:19 Speed:-2%
        * Ask (Light, Speed Bonus, Stamina Reduction)          Armor:28 Speed:+5%
        * Asksvin Cape (Speed Bonus, Stamina Reduction)        Armor:7  Speed:+7%
        * Flametal (Heavy, Dmg res)                            Armor:38 Speed:-5%
        * Ashen Cape (Armor)                                   Armor:16 Speed:+0%
    * Trinkets :
        * Heart of the Forest (50, Health Regen Bonus)
        * Bronze Pendant (50, Stamina Regen Bonus)
        * Iron Broach (65, Armor Bonus, Recover Health)
        * Nimble Anklet (65, Speed Bonus, Recover Stamina)
        * Fins of Destiny (10, Swim Bonus)
        * Wolf Sight (65, Archery Bonus, Spear Bonus, Pierce Damage Bonus)
        * Crystal Heart (75, Physical Damage Res)
        * Evasion Mantle (70, Dodge Bonus, Parry Bonus, Block Stamina Reduction)
        * Bracelets of the Brave (75, Club Bonus, Blunt Damage Bonus, Recover Health)
        * Resounding Shackle (75, Slash Damage Bonus, Revcover Stamina)
        * Pulsating Earings (80, Eitr Regen Bonus)
        * Brimstone (100, Recover Health, Recover Stamina)
        * Jormundling (85, Recover Eitr, Magic Bonus)
* Add crafting
* Add loot
    * Add moar loot
        * Pickable items on the ground
        * Chests
        * Creature drops
            * Resin
            * Neck Tail
            * Deer Hide
            * Deer Meat
            * Leather Scraps
            * Boar Meat
            * Feathers
            * **Hard Antler**
            * Greydwarf Eye
            * Ancient Seed
            * Troll Hide
            * Coins
            * Bear Hide
            * Bear Meat
            * Bear Paw
            * Bone Fragments
            * Ectoplasm
            * **Hildir's Brass Chest**
            * **Swamp Key**
            * Ooze
            * Entrails
            * Bloodbag
            * Guck
            * Root
            * Chain
            * Coal
            * Surtling Core
            * **Kvastur**
            * **Wishbone**
            * Wolf Pelt
            * Wolf Fang
            * Wolf Meat
            * Freeze Gland
            * Red Jute
            * Crystal
            * **Hildir's Silver Chest**
            * **Dragon Tear**
            * Black Metal Scrap
            * Lox Pelt
            * Lox Meat
            * Needle
            * Tar
            * Vile Ribcage
            * Fuling Totem
            * **Hildir's Bronze Chest**
            * **Torn Spirit**
            * Carapace
            * Seeker Meat
            * Hare Meat
            * Scale Hide
            * Mandible
            * Bilebag
            * Bloodclot
            * Royal Jelly
            * Black Marble
            * Soft Tissue
            * **Majestic Carapace**
            * Charred Bone
            * Volture Meat
            * Volture Egg
            * Asksvin Tail
            * Asksvin Hide
            * Asksvin Bladder
            * Sulfur
            * Proustite Powder
            * Charred Cogwheel
            * Celestial Feather
            * Morgan Sinew
            * Morgan Heart
            * Bonemaw Meat
            * Bonemaw Tooth
            * **Dyrnwyn Hilt Fragment**
            * **Fader Relic**
        * Other
        * Trophies
            * Boar Trophy                     (Common, 15%)
            * Neck Trophy                     (Common, 5%)
            * Deer Trophy                     (Common, 50%)
            * **Eikthyr Trophy**              (Boss, 100%)
            * Greydwarf Trophy                (Common, 5%)
            * Greydwarf Shaman Trophy         (Uncommon, 10%)
            * Greydwarf Brute Trophy          (Uncommon, 10%)
            * Skeleton Trophy                 (Common, 10%)
            * Ghost Trophy                    (Very Rare, 10%)
            * Rancid Remains Trophy           (Very Rare, 10%)
            * Troll Trophy                    (Rare, 50%)
            * Bear Trophy                     (Rare, 50%)
            * **Brenna Trophy**               (Miniboss, 100%)
            * **The Elder Trophy**            (Boss, 100%)
            * Serpent Trophy                  (Rare, 30%)
            * Draugr Trophy                   (Common, 10%)
            * Leech Trophy                    (Common, 10%)
            * Surtling Trophy                 (Common, 5%)
            * Draugr Elite Trophy             (Uncommon, 10%)
            * Abomination Trophy              (Rare, 30%)
            * Wraith Trophy                   (Very Rare, 5%)
            * **Kvastur**                     (Miniboss, 100%)
            * **Bonemass Trophy**             (Boss, 100%)
            * Wolf Trophy                     (Common, 10%)
            * Drake Trophy                    (Common, 10%)
            * Ulv Trophy                      (Common, 10%)
            * Fenring Trophy                  (Rare, 10%)
            * Cultist Trophy                  (Uncommon, 10%)
            * Stone Golem Trophy              (Very Rare, 5%)
            * **Geirrhafa Trophy**            (Miniboss, 100%)
            * **Moder Trophy**                (Boss, 100%)
            * Fuling Trophy                   (Common, 10%)
            * Fuling Shaman Trophy            (Rare, 10%)
            * Deathsquito Trophy              (Common, 5%)
            * Growth Trophy                   (Uncommon, 5%)
            * Lox Trophy                      (Uncommon, 10%)
            * Fuling Berserker Trophy         (Rare, 5%)
            * Vile Trophy                     (Very Rare, 10%)
            * **Zil Trophy**                  (Miniboss, 100%)
            * **Thungr Trophy**               (Miniboss, 100%)
            * **Yagluth Trophy**              (Boss, 100%)
            * Hare Trophy                     (Common, 5%)
            * Seeker Trophy                   (Common, 10%)
            * Tick Trophy                     (Common, 5%)
            * Dvergr Trophy                   (Uncommon, 5%)
            * Gjall Trophy                    (Very Rare, 30%)
            * Seeker Soldier Trophy           (Very Rare, 5%)
            * **The Queen Trophy**            (Boss, 100%)
            * Charred Warrior Trophy          (Common, 5%)
            * Charred Marksman Trophy         (Common, 5%)
            * Volture Trophy                  (Common, 10%)
            * Asksvin Trophy                  (Uncommon, 10%)
            * Bonemaw Trophy                  (Very Rare, 30%)
            * Morgen Trophy                   (Very Rare, 5%)
            * Fallen Valkyrie Trophy          (Very Rare, 5%)
            * Charred Warlock Trophy          (Very Rare, 5%)
            * **Fader Trophy**                (Boss, 100%)
* Add stamina bar
* Add food
* Add more foood
    * Food
        * Meadows
            Mushroom            Health:15  Stamina:15  Regen:+1
            Raspberry           Health:7   Stamina:20  Regen:+1
            Cooked Neck Tail    Health:25  Stamina:8   Regen:+2
            Cooked Boar Meat    Health:30  Stamina:10  Regen:+3
            Cooked Deer Meat    Health:35  Stamina:12  Regen:+3
            Honey               Health:8   Stamina:35  Regen:+1
        * Black Forest
            Blueberries         Health:8   Stamina:25  Regen:+1
            Yellow Mushroom     Health:10  Stamina:30  Regen:+1
            Carrot              Health:13  Stamina:40  Regen:+2
            Cooked Bear Meat    Health:40  Stamina:13  Regen:+4
            Carrot Soup         Health:17  Stamina:50  Regen:+2
            Queen's Jam         Health:15  Stamina:45  Regen:+2
            Deer Stew           Health:50  Stamina:17  Regen:+4
            Minced Meat Sauce   Health:45  Stamina:15  Regen:+3
            Boar Jerky          Health:23  Stamina:23  Regen:+4
        * Swamp
            Muckshake           Health:17  Stamina:50  Regen:+2
            Turnip Stew         Health:19  Stamina:55  Regen:+3
            Black Soup          Health:50  Stamina:17  Regen:+5
            Sausages            Health:55  Stamina:19  Regen:+5
            Cooked Fish         Health:50  Stamina:17  Regen:+4
            Cooked Serpent Meat Health:70  Stamina:24  Regen:+6
            Serpent Stew        Health:80  Stamina:27  Regen:+7
        * Mountain
            Cooked Wolf Meat    Health:40  Stamina:14  Regen:+4
            Onion               Health:14  Stamina:40  Regen:+2
            Wolf Skewer         Health:65  Stamina:22  Regen:+5
            Onion Soup          Health:20  Stamina:60  Regen:+3
            Eyescream           Health:22  Stamina:65  Regen:+3
            Wolf Jerky          Health:31  Stamina:31  Regen:+4
            Cooked Serpent Meat Health:70  Stamina:24  Regen:+6
            Serpent Stew        Health:80  Stamina:27  Regen:+7
        * Plains
            Cloudberries        Health:15  Stamina:45  Regen:+2
            Cooked Lox Meat     Health:50  Stamina:17  Regen:+4
            Bread               Health:23  Stamina:70  Regen:+3
            Blood Pudding       Health:25  Stamina:75  Regen:+3
            Lox Meat Pie        Health:75  Stamina:25  Regen:+5
            Fish Wraps          Health:70  Stamina:24  Regen:+5
            Frosted Sweetbread  Health:43  Stamina:43  Regen:+4
            Cooked Serpent Meat Health:70  Stamina:24  Regen:+6
            Serpent Stew        Health:80  Stamina:27  Regen:+7
            Cooked Egg          Health:35  Stamina:12  Regen:+3
            Cooked Chicken Meat Health:60  Stamina:20  Regen:+5
        * Mistlands
            Cooked Egg          Health:
            Cooked Chicken Meat 
            Jotun Puffs         
            Magecap             
            Cooked Hare Meat    
            Cooked Seeker Meat  
            Meat Platter        
            Misthare Supreme    
            Mushroom Omelette   
            Salad               
            
        * Ashlands

* Add shields
    * Shields :
        * Wooden Shield
        * Wooden Tower Shield
        * Bronze Buckler
        * Bone Tower Shield
        * Iron Buckler
        * Banded Shield
        * Iron Tower Shield
        * Silver Shield
        * Serpent Scale Shield
        * Black Metal Shield
        * Black Metal Tower Shield
        * Carapace Buckler
        * Carapace Shield
        * Flametal Shield
        * Flametal Tower Shield
* Add parrying and staggering
* Add dodging
* Add levels
    * Loot Tables
        * Meadows
            * Neck
                1 Neck Tail
                5% Neck Trophy
            * Greyling
                1 Resin
            * Boar
                1 Boar Meat
                1 Leather Scraps
                15% Boar Trophy
            * Deer
                1 Deer Meat
                1 Deer Hide
                50% Deer Trophy
            * Beech Tree
                3 rolls
                    50% 1 Wood
                    50% 2 Wood
                2 rolls
                    50% 1 Resin
            * Birch Tree
                3 rolls
                    50% 1 Wood
                    50% 2 Wood
                2 rolls
                    50% 1 Finewood
                    50% 2 Finewood
                2 rolls
                    50% Resin
            * Rock
                2 rolls
                    50% 1 Stone
                    50% 2 Stone
                    50% 3 Stone
            * Eikthyr
                1 Eikthyr Trophy
                3 Hard Antler
            * Fir Tree
                3 rolls
                    50% 1 Wood
                    50% 2 Wood
                2 rolls
                    50% 1 Corewood
                    50% 2 Corewood
                2 rolls
                    50% 1 Resin
            * Copper Deposit
                2 rolls
                    50% 1 Copper Ore
                    50% 2 Copper Ore
            * Tin Deposit
                3 rolls
                    25% 1 Tin Ore
                    50% 2 Tin Ore
                    25% 3 Tin Ore
            * Burial Chambers Chest
                2 rolls
                    50% 1 Amber Pearl
                    25% 2 Amber Pearl
                6 rolls
                    10% 1 Coins
                    15% 2 Coins
                    30% 3 Coins
                    25% 4 Coins
                    10% 5 Coins
                    10% 6 Coins
                2 rolls
                    50% 1 Ruby
                    10% 2 Ruby
                3 rolls
                    60% 1 Amber
                    10% 2 Amber
            * Troll Cave
            * *Smoldering Tomb*
            * Sunken Crypt
            * Frost Cave
            * *Howling Caverns*
            * Fuling Village
            * *Sealed Tower*
            * 
            * 
            * 
    * Each level is in a certain biome. Biomes each have different loot, enemies, crafting recipes, and terrain. If a level is completed by finding the loot and exploring the dungeon fully, then the character progresses to the next level. If the character dies on a level, they are reverted to the start of that level. On game start, either a game that is in progress is selected, or a new game is started.
    * Levels are as follows

        1 Meadows
        2 ***Eikthyr Bossfight***
        3 Black Forest
        4 *Burial Chambers*
        5 *Troll Cave*
        6 Black Forest
        7 **Smoldering Tomb (Brenna)**
        8 ***The Elder Bossfight***
        9 Ocean (exploration)
        10 Swamps
        11 *Sunken Crypts*
        12 Swamps
        13 ***Bonemass Bossfight***
        14 Ocean 2
        15 Mountains
        16 *Ice Caves*
        17 Mountains
        18 **Howling Caverns (Geirrhafa)**
        19 ***Moder Bossfight***
        20 Ocean 3
        21 Plains
        22 *Fuling Village*
        23 Plains
        24 **Sealed Tower (Zil and Thungr)**
        25 ***Yagluth Bossfight***
        26 Ocean 4
        27 Mistlands Coast
        28 Mistlands
        29 *Dvergr Outpost*
        30 Mistlands
        31 Giant Remains
        32 *Infested Mines (Dvergr Tower)*
        33 *Infested Mines (Cliffside)*
        34 Mistlands
        35 ***The Queen Bossfight***
        36 Ocean 5
        37 Ashlands Waters
        38 Ashlands Coast
        39 Ashlands
        40 *Putrid Hole*
        41 Ashlands
        42 Ashlands (Inland)
        43 *Charred Fortress*
        44 Ashlands
        45 *Putrid Hole*
        46 *Putrid Hole*
        47 Ashlands
        48 *Charred Fortress*
        49 Ashlands
        50 **First Mysterious Location**
        51 Putrid Hole
        52 **Second Mysterious Location**
        53 Ashlands
        54 **Tomb of Lord Reto (Lord Reto)**
        55 Ashlands
        56 ***Fader Bossfight***