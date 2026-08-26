"""
services/demo_data.py

A small, self-contained sample tour so the app can be run and tested
immediately without needing a real museum's content database.
"""

SAMPLE_TOUR_SPEC = {
    "tour_id": "T-001",
    "title": "Highlights of Modern Art",
    "theme": "modern_art",
    "language": "en",
    "stops": [
        {
            "name": "Entrance Hall",
            "location_id": "B-01",
            "order": 1,
            "description": (
                "Your tour begins here. Ama Boateng greets you and explains how "
                "your tablet will recognize each room as you walk through the gallery."
            ),
            "description_translations": {
                "fr": (
                    "Votre visite commence ici. Ama Boateng vous accueille et vous "
                    "explique comment votre tablette reconnaîtra chaque salle."
                ),
            },
            "media": {
                "images": [
                    {"path": "assets/images/entrance_hall_1.jpg", "caption": "The museum's main entrance hall"},
                ],
                "video_path": "assets/video/entrance_hall.mp4",
                "audio_path": "assets/audio/welcome.mp3",
                "audio_path_translations": {"fr": "assets/audio/welcome_fr.mp3"},
            },
            "content_type": "audio",
            "content_kwargs": {
                "title": "Welcome",
                "duration_seconds": 16,
                "narrator": "Ama Boateng",
                "script": (
                    "Welcome to Highlights of Modern Art. I'm Ama Boateng, and "
                    "I'll be your guide today. As you walk through this gallery, "
                    "your tablet will recognize which room you're in and share "
                    "the story behind each piece. Let's begin in the Cubism "
                    "Room, just ahead of you."
                ),
                "audio_path": "assets/audio/welcome.mp3",
                "translations": {
                    "fr": {
                        "title": "Bienvenue",
                    },
                },
            },
        },
        {
            "name": "Cubism Room",
            "location_id": "B-02",
            "order": 2,
            "description": (
                "Discover how Picasso and Braque shattered traditional perspective, "
                "painting subjects from several angles at once."
            ),
            "description_translations": {
                "fr": (
                    "Découvrez comment Picasso et Braque ont brisé la perspective "
                    "traditionnelle, peignant les sujets sous plusieurs angles à la fois."
                ),
            },
            "media": {
                "images": [
                    {"path": "assets/images/cubism_artwork.jpg", "caption": "A Cubist painting on display"},
                    {"path": "assets/images/cubism_room_2.jpg", "caption": "The Cubism Room gallery space"},
                ],
                "video_path": "assets/video/cubism_room.mp4",
                "audio_path": "assets/audio/cubism_room.mp3",
                "audio_path_translations": {"fr": "assets/audio/cubism_room_fr.mp3"},
            },
            "content_type": "video",
            "content_kwargs": {
                "title": "Breaking the Frame: Cubism Explained",
                "duration_seconds": 10,
                "frames_dir": "assets/video_frames/cubism_room",
                "frame_count": 20,
                "caption": "Breaking the Frame: Cubism Explained",
                "translations": {
                    "fr": {
                        "title": "Briser le Cadre : le Cubisme Expliqué",
                    },
                },
            },
        },
        {
            "name": "Sculpture Garden",
            "location_id": "GPS-01",
            "order": 3,
            "description": (
                "Step outside to explore large-scale works in stone and welded "
                "steel, arranged to be viewed from many angles as you walk the path."
            ),
            "description_translations": {
                "fr": (
                    "Sortez pour explorer des œuvres à grande échelle en pierre et "
                    "en acier soudé, disposées pour être vues sous plusieurs angles."
                ),
            },
            "media": {
                "images": [
                    {"path": "assets/images/sculpture_garden_1.jpg", "caption": "A stone sculpture in the garden"},
                    {"path": "assets/images/sculpture_garden_2.jpg", "caption": "A welded-steel sculpture"},
                ],
                "video_path": "assets/video/sculpture_garden.mp4",
                "audio_path": "assets/audio/sculpture_garden.mp3",
                "audio_path_translations": {"fr": "assets/audio/sculpture_garden_fr.mp3"},
            },
            "content_type": "text",
            "content_kwargs": {
                "title": "Stone and Steel",
                "body": (
                    "This outdoor garden features large-scale works in stone "
                    "and welded steel, arranged to be viewed from multiple "
                    "angles as visitors walk the path."
                ),
                "translations": {
                    "fr": {
                        "title": "Pierre et Acier",
                        "body": (
                            "Ce jardin extérieur présente des œuvres à grande "
                            "échelle en pierre et en acier soudé, disposées pour "
                            "être vues sous plusieurs angles le long du chemin."
                        ),
                    },
                },
            },
        },
        {
            "name": "Contemporary Wing",
            "location_id": "B-03",
            "order": 4,
            "description": (
                "The final stop: living artists exploring identity, technology, "
                "and community through contemporary works."
            ),
            "description_translations": {
                "fr": (
                    "Dernier arrêt : des artistes vivants qui explorent "
                    "l'identité, la technologie et la communauté."
                ),
            },
            "media": {
                "images": [
                    {"path": "assets/images/contemporary_wing_1.jpg", "caption": "A piece from the Contemporary Wing"},
                    {"path": "assets/images/contemporary_wing_2.jpg", "caption": "The Contemporary Wing gallery space"},
                ],
                "video_path": "assets/video/contemporary_wing.mp4",
                "audio_path": "assets/audio/voices_of_now.mp3",
                "audio_path_translations": {"fr": "assets/audio/voices_of_now_fr.mp3"},
            },
            "content_type": "audio",
            "content_kwargs": {
                "title": "Voices of Now",
                "duration_seconds": 25,
                "narrator": "Kwame Asante",
                "script": (
                    "You've reached the Contemporary Wing, the final stop on "
                    "today's tour. I'm Kwame Asante. The pieces in this room "
                    "were created by living artists who are actively shaping "
                    "how we think about identity, technology, and community "
                    "today. Take your time here, and notice how differently "
                    "each artist approaches the same big questions. Thank you "
                    "for joining us, and we hope you'll visit again soon."
                ),
                "translations": {
                    "fr": {
                        "title": "Voix d'Aujourd'hui",
                    },
                },
                "audio_path": "assets/audio/voices_of_now.mp3",
            },
        },
    ],
}

# location_id -> (lat, lon), used only by the GPS simulator for the
# one outdoor stop in the sample tour above.
GPS_KNOWN_POINTS = {
    "GPS-01": (5.6037, -0.1870),
    "B-03": (5.6040, -0.1875),
}

# location_id -> (x, y) position on the simplified floor-plan grid used
# by the interactive map widget. Coordinates are plain 0-100 percentages
# of the floor plan canvas, not real-world measurements.
FLOOR_PLAN_POSITIONS = {
    "B-01": (10, 50),
    "B-02": (35, 20),
    "GPS-01": (60, 80),
    "B-03": (85, 50),
    "T-01": (15, 25),
    "T-02": (40, 60),
    "T-03": (60, 25),
    "T-04": (80, 70),
    "T-05": (85, 30),
    "T-06": (50, 82),
}

# Room labels for the generated floor-plan background image (see
# services/floorplan_generator.py), keyed by the same location_ids
# used above — drawn as the "room" each stop sits inside.
FLOOR_PLAN_ROOM_LABELS = {
    "B-01": "Entrance Hall",
    "B-02": "Cubism Room",
    "GPS-01": "Sculpture Garden",
    "B-03": "Contemporary Wing",
    "T-01": "Titanic Exhibit",
    "T-02": "Jewel Case",
    "T-03": "Greece Gallery",
    "T-04": "Egyptian Wing",
    "T-05": "Memorial Room",
    "T-06": "Restoration Lab",
}

# A second sample tour built from real uploaded exhibit photographs,
# demonstrating the ImageGuide and ModelGuide content types.
TREASURES_TOUR_SPEC = {
    "tour_id": "T-002",
    "title": "Treasures Through Time",
    "theme": "history_and_antiquities",
    "language": "en",
    "stops": [
        {
            "name": "The Heart of the Ocean",
            "location_id": "T-01",
            "order": 1,
            "description": (
                "A dazzling sapphire-and-diamond pendant, one of the most "
                "photographed pieces in the exhibit."
            ),
            "description_translations": {
                "fr": (
                    "Un pendentif saphir et diamant éblouissant, l'une des "
                    "pièces les plus photographiées de l'exposition."
                ),
            },
            "media": {
                "images": [
                    {"path": "assets/images/heart_of_ocean_necklace.jpg", "caption": "The Heart of the Ocean necklace"},
                    {"path": "assets/images/heart_of_ocean_2.jpg", "caption": "Detail of the sapphire pendant"},
                ],
                "video_path": "assets/video/heart_of_ocean.mp4",
                "audio_path": "assets/audio/heart_of_ocean.mp3",
                "audio_path_translations": {"fr": "assets/audio/heart_of_ocean_fr.mp3"},
            },
            "content_type": "image",
            "content_kwargs": {
                "title": "Heart of the Ocean Necklace",
                "image_path": "assets/images/heart_of_ocean_necklace.jpg",
                "caption": "A replica of the famous sapphire-and-diamond necklace "
                           "displayed from the Titanic exhibit.",
                "duration_seconds": 25,
                "translations": {
                    "fr": {
                        "title": "Collier Coeur de l'Océan",
                        "caption": "Une réplique du célèbre collier de saphir et "
                                   "diamants exposé dans le cadre de l'exposition Titanic.",
                    },
                },
            },
        },
        {
            "name": "Victorian Jewel Case",
            "location_id": "T-02",
            "order": 2,
            "description": (
                "A gold necklace with a heart-shaped pendant, displayed on a "
                "velvet bust from the Victorian era."
            ),
            "description_translations": {
                "fr": (
                    "Un collier en or avec un pendentif en forme de cœur, "
                    "présenté sur un buste en velours de l'époque victorienne."
                ),
            },
            "media": {
                "images": [
                    {"path": "assets/images/heart_pendant_necklace.jpg", "caption": "The heart pendant necklace"},
                    {"path": "assets/images/victorian_jewel_case_2.jpg", "caption": "The Victorian jewel case display"},
                ],
                "video_path": "assets/video/victorian_jewel_case.mp4",
                "audio_path": "assets/audio/victorian_jewel_case.mp3",
                "audio_path_translations": {"fr": "assets/audio/victorian_jewel_case_fr.mp3"},
            },
            "content_type": "image",
            "content_kwargs": {
                "title": "Heart Pendant Necklace",
                "image_path": "assets/images/heart_pendant_necklace.jpg",
                "caption": "A gold necklace with a heart-shaped pendant, "
                           "displayed on a velvet bust.",
                "duration_seconds": 20,
                "translations": {
                    "fr": {
                        "title": "Collier Pendentif Coeur",
                        "caption": "Un collier en or avec un pendentif en forme de "
                                   "coeur, présenté sur un buste en velours.",
                    },
                },
            },
        },
        {
            "name": "Ancient Greece Gallery",
            "location_id": "T-03",
            "order": 3,
            "description": (
                "A terracotta water jar decorated in the black-figure "
                "technique, once used in everyday ancient Greek life."
            ),
            "description_translations": {
                "fr": (
                    "Une jarre à eau en terre cuite décorée selon la "
                    "technique des figures noires."
                ),
            },
            "media": {
                "images": [
                    {"path": "assets/images/greek_hydria_vase.jpg", "caption": "The black-figure hydria"},
                    {"path": "assets/images/greek_gallery_2.jpg", "caption": "The Ancient Greece Gallery"},
                ],
                "video_path": "assets/video/ancient_greece_gallery.mp4",
                "audio_path": "assets/audio/ancient_greece_gallery.mp3",
                "audio_path_translations": {"fr": "assets/audio/ancient_greece_gallery_fr.mp3"},
            },
            "content_type": "image",
            "content_kwargs": {
                "title": "Black-Figure Hydria",
                "image_path": "assets/images/greek_hydria_vase.jpg",
                "caption": "A terracotta water jar decorated in the "
                           "black-figure technique.",
                "duration_seconds": 25,
                "translations": {
                    "fr": {
                        "title": "Hydrie à Figures Noires",
                        "caption": "Une jarre à eau en terre cuite décorée selon "
                                   "la technique des figures noires.",
                    },
                },
            },
        },
        {
            "name": "Egyptian Wing",
            "location_id": "T-04",
            "order": 4,
            "description": (
                "The painted limestone bust of Queen Nefertiti, one of the "
                "most copied works of ancient Egypt."
            ),
            "description_translations": {
                "fr": (
                    "Le buste en calcaire peint de la reine Néfertiti, l'une "
                    "des œuvres les plus copiées de l'Égypte antique."
                ),
            },
            "media": {
                "images": [
                    {"path": "assets/images/nefertiti_bust.jpg", "caption": "The bust of Nefertiti"},
                    {"path": "assets/images/egyptian_wing_2.jpg", "caption": "The Egyptian Wing gallery"},
                ],
                "video_path": "assets/video/egyptian_wing.mp4",
                "audio_path": "assets/audio/egyptian_wing.mp3",
                "audio_path_translations": {"fr": "assets/audio/egyptian_wing_fr.mp3"},
            },
            "content_type": "image",
            "content_kwargs": {
                "title": "Bust of Nefertiti",
                "image_path": "assets/images/nefertiti_bust.jpg",
                "caption": "The painted limestone bust of Queen Nefertiti, "
                           "one of the most copied works of ancient Egypt.",
                "duration_seconds": 25,
                "translations": {
                    "fr": {
                        "title": "Buste de Néfertiti",
                        "caption": "Le buste en calcaire peint de la reine "
                                   "Néfertiti, l'une des oeuvres les plus copiées "
                                   "de l'Égypte antique.",
                    },
                },
            },
        },
        {
            "name": "Titanic Memorial Room",
            "location_id": "T-05",
            "order": 5,
            "description": (
                "The life jacket worn by Madeleine Talmage Astor during the "
                "Titanic's sinking, a quiet, powerful memorial piece."
            ),
            "description_translations": {
                "fr": (
                    "Le gilet de sauvetage porté par Madeleine Talmage Astor "
                    "lors du naufrage du Titanic."
                ),
            },
            "media": {
                "images": [
                    {"path": "assets/images/titanic_life_jacket.jpg", "caption": "Madeleine Astor's life jacket"},
                    {"path": "assets/images/titanic_memorial_room_2.jpg", "caption": "The Titanic Memorial Room"},
                ],
                "video_path": "assets/video/titanic_memorial_room.mp4",
                "audio_path": "assets/audio/titanic_memorial_room.mp3",
                "audio_path_translations": {"fr": "assets/audio/titanic_memorial_room_fr.mp3"},
            },
            "content_type": "image",
            "content_kwargs": {
                "title": "Madeleine Astor's Life Jacket",
                "image_path": "assets/images/titanic_life_jacket.jpg",
                "caption": "The life jacket worn by Madeleine Talmage Astor, "
                           "the 18-year-old bride of John Jacob Astor, during "
                           "the Titanic's sinking.",
                "duration_seconds": 30,
                "translations": {
                    "fr": {
                        "title": "Gilet de Sauvetage de Madeleine Astor",
                        "caption": "Le gilet de sauvetage porté par Madeleine "
                                   "Talmage Astor, la jeune épouse de 18 ans de "
                                   "John Jacob Astor, lors du naufrage du Titanic.",
                    },
                },
            },
        },
        {
            "name": "Digital Restoration Lab",
            "location_id": "T-06",
            "order": 6,
            "description": (
                "See how conservators use 3D scanning to study and preserve "
                "fragile artifacts like the hydria vase without touching them."
            ),
            "description_translations": {
                "fr": (
                    "Découvrez comment les restaurateurs utilisent la "
                    "numérisation 3D pour étudier et préserver des objets fragiles."
                ),
            },
            "media": {
                "images": [
                    {"path": "assets/images/digital_restoration_lab_1.jpg", "caption": "Inside the restoration lab"},
                ],
                "video_path": "assets/video/digital_restoration_lab.mp4",
                "audio_path": "assets/audio/digital_restoration_lab.mp3",
                "audio_path_translations": {"fr": "assets/audio/digital_restoration_lab_fr.mp3"},
            },
            "content_type": "model",
            "content_kwargs": {
                "title": "Hydria Vase (3D Scan)",
                "model_path": "assets/models/greek_hydria_vase.glb",
                "format": "glb",
                "duration_seconds": 45,
            },
        },
    ],
}

# Sample quizzes attached to specific stops of the Treasures tour,
# demonstrating the Quiz / Collectible gamification models.
from models.quiz import QuizQuestion, Quiz, Collectible  # noqa: E402

# Quizzes for the "Highlights of Modern Art" tour (SAMPLE_TOUR_SPEC),
# keyed by that tour's own location_ids.
SAMPLE_TOUR_QUIZZES = {
    "B-01": Quiz(
        quiz_id="Q-M01",
        location_id="B-01",
        questions=[
            QuizQuestion(
                "Who welcomes visitors at the start of this tour?",
                ["Ama Boateng", "Kwame Asante", "Nefertiti"],
                correct_index=0,
            ),
            QuizQuestion(
                "What is the name of this tour?",
                ["Highlights of Modern Art", "Treasures Through Time", "Voices of Now"],
                correct_index=0,
            ),
            QuizQuestion(
                "Which room does the guide say you're heading to next?",
                ["The Cubism Room", "The Sculpture Garden", "The Contemporary Wing"],
                correct_index=0,
            ),
        ],
        collectible=Collectible("C-M01", "Welcome Ribbon", "A digital ribbon marking the start of your tour."),
    ),
    "B-02": Quiz(
        quiz_id="Q-M02",
        location_id="B-02",
        questions=[
            QuizQuestion(
                "Cubism is best known for breaking subjects into:",
                ["Geometric, fragmented shapes", "Soft, blended brushstrokes", "Photorealistic detail"],
                correct_index=0,
            ),
            QuizQuestion(
                "Cubism emerged in the early:",
                ["20th century", "16th century", "19th century BCE"],
                correct_index=0,
            ),
            QuizQuestion(
                "Which pair of artists is most closely associated with founding Cubism?",
                ["Pablo Picasso and Georges Braque", "Claude Monet and Edgar Degas", "Michelangelo and Raphael"],
                correct_index=0,
            ),
        ],
        collectible=Collectible("C-M02", "Fractured Frame Badge", "A digital badge shaped like a cubist frame."),
    ),
    "GPS-01": Quiz(
        quiz_id="Q-M03",
        location_id="GPS-01",
        questions=[
            QuizQuestion(
                "The Sculpture Garden is best described as:",
                ["An outdoor space with stone and steel works", "An indoor hall of paintings", "A gift shop"],
                correct_index=0,
            ),
            QuizQuestion(
                "The sculptures here are meant to be viewed:",
                ["From multiple angles while walking the path", "Only from directly in front", "Only from above"],
                correct_index=0,
            ),
            QuizQuestion(
                "Alongside stone, which other material is featured in this garden?",
                ["Welded steel", "Blown glass", "Woven textile"],
                correct_index=0,
            ),
        ],
        collectible=Collectible("C-M03", "Garden Path Pin", "A digital pin shaped like a garden pathway."),
    ),
    "B-03": Quiz(
        quiz_id="Q-M04",
        location_id="B-03",
        questions=[
            QuizQuestion(
                "Who narrates the Contemporary Wing stop?",
                ["Kwame Asante", "Ama Boateng", "A recorded museum announcement"],
                correct_index=0,
            ),
            QuizQuestion(
                "The artists featured in this wing are described as:",
                ["Living artists shaping ideas today", "Artists from ancient Egypt", "Anonymous medieval painters"],
                correct_index=0,
            ),
            QuizQuestion(
                "This stop is described as:",
                ["The final stop on the tour", "The first stop on the tour", "An optional detour"],
                correct_index=0,
            ),
        ],
        collectible=Collectible("C-M04", "Now Badge", "A digital badge marking completion of the tour."),
    ),
}

TREASURES_QUIZZES = {
    "T-01": Quiz(
        quiz_id="Q-01",
        location_id="T-01",
        questions=[
            QuizQuestion(
                "What is the 'Heart of the Ocean' necklace famously associated with?",
                ["The Titanic", "The Mona Lisa", "Ancient Rome"],
                correct_index=0,
            ),
            QuizQuestion(
                "The gemstone at the center of the Heart of the Ocean design is a:",
                ["Sapphire", "Ruby", "Emerald"],
                correct_index=0,
            ),
            QuizQuestion(
                "The necklace shown here is best described as a:",
                ["Replica inspired by the film and exhibit", "The original 1912 piece", "A modern royal commission"],
                correct_index=0,
            ),
            QuizQuestion(
                "What shape is the pendant cut into?",
                ["A heart", "A star", "A teardrop"],
                correct_index=0,
            ),
            QuizQuestion(
                "The smaller stones surrounding the pendant are:",
                ["Diamonds", "Pearls", "Opals"],
                correct_index=0,
            ),
        ],
        collectible=Collectible("C-01", "Sapphire Pin", "A digital pin shaped like the famous necklace."),
    ),
    "T-02": Quiz(
        quiz_id="Q-03",
        location_id="T-02",
        questions=[
            QuizQuestion(
                "In Victorian jewelry, a heart-shaped pendant most commonly symbolized what?",
                ["Love or remembrance", "Military rank", "Royal decree"],
                correct_index=0,
            ),
            QuizQuestion(
                "What metal is the necklace's chain made of?",
                ["Gold", "Silver", "Platinum"],
                correct_index=0,
            ),
            QuizQuestion(
                "The necklace is displayed resting on:",
                ["A velvet bust", "A glass shelf", "A mannequin's wrist"],
                correct_index=0,
            ),
            QuizQuestion(
                "Victorian mourning jewelry often incorporated which material to honor the deceased?",
                ["Human hair", "Ivory", "Coral"],
                correct_index=0,
            ),
            QuizQuestion(
                "Which era is 'Victorian' jewelry named after?",
                ["The reign of Queen Victoria", "The reign of Queen Elizabeth I", "The French Revolution"],
                correct_index=0,
            ),
        ],
        collectible=Collectible("C-03", "Locket Charm", "A digital charm shaped like a heart locket."),
    ),
    "T-03": Quiz(
        quiz_id="Q-02",
        location_id="T-03",
        questions=[
            QuizQuestion(
                "The black-figure technique originated in which ancient civilization?",
                ["Ancient Greece", "Ancient Egypt", "The Roman Empire"],
                correct_index=0,
            ),
            QuizQuestion(
                "A 'hydria' was traditionally used by ancient Greeks to carry:",
                ["Water", "Wine", "Olive oil"],
                correct_index=0,
            ),
            QuizQuestion(
                "In the black-figure technique, figures are painted in black against a background of:",
                ["The natural orange clay", "White plaster", "Blue glaze"],
                correct_index=0,
            ),
            QuizQuestion(
                "What material is this hydria made from?",
                ["Terracotta (fired clay)", "Bronze", "Marble"],
                correct_index=0,
            ),
            QuizQuestion(
                "The handles on a hydria typically number:",
                ["Three (two side, one back)", "Two", "Four"],
                correct_index=0,
            ),
        ],
        collectible=Collectible("C-02", "Amphora Badge", "A digital badge shaped like a Greek vase."),
    ),
    "T-04": Quiz(
        quiz_id="Q-04",
        location_id="T-04",
        questions=[
            QuizQuestion(
                "The Bust of Nefertiti is one of the most copied works of which ancient civilization?",
                ["Ancient Egypt", "Ancient Greece", "Ancient Mesopotamia"],
                correct_index=0,
            ),
            QuizQuestion(
                "Nefertiti was the queen consort of which pharaoh?",
                ["Akhenaten", "Tutankhamun", "Ramesses II"],
                correct_index=0,
            ),
            QuizQuestion(
                "The bust is primarily made of:",
                ["Painted limestone", "Solid gold", "Carved obsidian"],
                correct_index=0,
            ),
            QuizQuestion(
                "The tall blue headdress Nefertiti wears is known as a:",
                ["Crown/cap (a distinctive flat-topped headdress)", "Turban", "Veil"],
                correct_index=0,
            ),
            QuizQuestion(
                "One notable feature of the bust is that it is missing:",
                ["The inlay of the left eye", "Its nose", "Its ears"],
                correct_index=0,
            ),
        ],
        collectible=Collectible("C-04", "Nefertiti Crown Pin", "A digital pin shaped like Nefertiti's crown."),
    ),
    "T-05": Quiz(
        quiz_id="Q-05",
        location_id="T-05",
        questions=[
            QuizQuestion(
                "Madeleine Astor's life jacket is displayed as a memorial to which historical event?",
                ["The sinking of the Titanic", "World War I", "The California Gold Rush"],
                correct_index=0,
            ),
            QuizQuestion(
                "Madeleine Astor was the wife of which wealthy passenger?",
                ["John Jacob Astor", "J.P. Morgan", "Andrew Carnegie"],
                correct_index=0,
            ),
            QuizQuestion(
                "What material were early 20th-century life jackets like this one typically made of?",
                ["Cork or kapok padding wrapped in canvas", "Inflatable rubber", "Foam plastic"],
                correct_index=0,
            ),
            QuizQuestion(
                "The Titanic sank after striking:",
                ["An iceberg", "A reef", "Another ship"],
                correct_index=0,
            ),
            QuizQuestion(
                "In what year did the Titanic sink?",
                ["1912", "1898", "1925"],
                correct_index=0,
            ),
        ],
        collectible=Collectible("C-05", "Life Jacket Pin", "A small digital pin honoring the Titanic memorial."),
    ),
    "T-06": Quiz(
        quiz_id="Q-06",
        location_id="T-06",
        questions=[
            QuizQuestion(
                "What is the main purpose of 3D-scanning an artifact like the hydria vase?",
                ["Digital preservation and study without touching the original",
                 "To replace the original with a print",
                 "To determine the artifact's market price"],
                correct_index=0,
            ),
            QuizQuestion(
                "A common file format for storing 3D scanned models (like the one used here) is:",
                ["GLB", "MP3", "CSV"],
                correct_index=0,
            ),
            QuizQuestion(
                "3D scanning lets researchers examine an artifact's surface detail without:",
                ["Physically handling the fragile original", "Taking any photographs", "Using any lighting"],
                correct_index=0,
            ),
            QuizQuestion(
                "Digital 3D models of artifacts can be especially useful for:",
                ["Remote study and virtual exhibits", "Replacing the need for museums entirely", "Melting down originals"],
                correct_index=0,
            ),
            QuizQuestion(
                "What technology is commonly used to capture the geometry of an artifact in 3D scanning?",
                ["Laser or structured-light scanners", "Standard flatbed scanners", "Metal detectors"],
                correct_index=0,
            ),
        ],
        collectible=Collectible("C-06", "Digital Scan Badge", "A badge marking completion of the restoration lab."),
    ),
}

# Combined lookup across every built-in tour, keyed by location_id.
# location_ids never collide across tours (B-*/GPS-* vs T-*), so a
# single dict safely covers all of them. Previously the UI passed
# TREASURES_QUIZZES alone to QuizObserver regardless of which tour was
# active, so the Modern Art tour's stops (different location_ids)
# could never match and no quiz ever triggered there.
ALL_QUIZZES = {**SAMPLE_TOUR_QUIZZES, **TREASURES_QUIZZES}

# Registry of built-in tours available for selection at launch, used by
# the Tour Selection screen (ui/app.py) so a visitor can choose which
# tour to follow rather than always loading one hardcoded tour.
BUILTIN_TOURS = {
    SAMPLE_TOUR_SPEC["tour_id"]: SAMPLE_TOUR_SPEC,
    TREASURES_TOUR_SPEC["tour_id"]: TREASURES_TOUR_SPEC,
}


def available_tour_summaries(offline_store=None):
    """
    Returns a list of (tour_id, title, theme, stop_count) tuples for
    every built-in tour, plus any additional tours saved in the
    offline store (e.g. created through the Admin CMS), for display
    on the Tour Selection screen.
    """
    summaries = [
        (spec["tour_id"], spec["title"], spec["theme"], len(spec["stops"]))
        for spec in BUILTIN_TOURS.values()
    ]
    if offline_store is not None:
        seen_ids = {s[0] for s in summaries}
        for tour_id in offline_store.list_downloaded_tours():
            if tour_id in seen_ids:
                continue
            try:
                tour = offline_store.load_tour(tour_id)
                summaries.append((tour.tour_id, tour.title, tour.theme, len(tour.stops)))
            except KeyError:
                continue
    return summaries
