"""
services/i18n.py

Translation table for the app's static UI chrome (button labels,
headers, status text) — separate from the per-exhibit content
translations already carried on each TourContent object (see
models/content.py, `_localized`).

Previously only exhibit content (title/caption/body/script) changed
when the visitor toggled language; the surrounding UI (buttons,
labels, headers) stayed in English no matter what. tr() gives every
screen a single place to look up the right string for the visitor's
current language, so the whole interface — not just the exhibit text
— changes together.
"""

UI_STRINGS = {
    "choose_a_tour": {"en": "Choose a Tour", "fr": "Choisir une Visite"},
    "language_label": {"en": "Language:", "fr": "Langue :"},
    "start_tour": {"en": "Start Tour", "fr": "Commencer la Visite"},
    "stops_suffix": {"en": "stops", "fr": "arrêts"},
    "back_to_tours": {"en": "< Tours", "fr": "< Visites"},
    "tap_a_stop": {
        "en": "Tap a stop below to simulate arriving there.",
        "fr": "Touchez un arrêt ci-dessous pour simuler votre arrivée.",
    },
    "drag_to_rotate": {
        "en": "Drag to rotate the model",
        "fr": "Faites glisser pour faire pivoter le modèle",
    },
    "play_narration": {"en": "\u25b6 Play Narration", "fr": "\u25b6 Lire la Narration"},
    "pause_narration": {"en": "\u23f8 Pause Narration", "fr": "\u23f8 Suspendre la Narration"},
    "play_video": {"en": "Play Video", "fr": "Lire la Vidéo"},
    "pause_video": {"en": "Pause Video", "fr": "Suspendre la Vidéo"},
    "media_button": {"en": "\U0001f4f7 Media", "fr": "\U0001f4f7 Médias"},
    "media_title": {"en": "Media", "fr": "Médias"},
    "media_tab_photos": {"en": "Photos", "fr": "Photos"},
    "media_tab_video": {"en": "Video", "fr": "Vidéo"},
    "media_tab_audio": {"en": "Audio", "fr": "Audio"},
    "media_prev": {"en": "\u2039 Prev", "fr": "\u2039 Préc."},
    "media_next": {"en": "Next \u203a", "fr": "Suiv. \u203a"},
    "media_photo_count": {"en": "Photo {i} of {n}", "fr": "Photo {i} sur {n}"},
    "media_no_photos": {"en": "Photos for this stop haven't been added yet.",
                         "fr": "Les photos de cet arrêt n'ont pas encore été ajoutées."},
    "media_no_video": {"en": "The video for this stop hasn't been added yet.",
                        "fr": "La vidéo de cet arrêt n'a pas encore été ajoutée."},
    "media_no_audio": {"en": "The audio for this stop hasn't been added yet.",
                        "fr": "L'audio de cet arrêt n'a pas encore été ajouté."},
    "media_play_video": {"en": "\u25b6 Play Video", "fr": "\u25b6 Lire la Vidéo"},
    "media_pause_video": {"en": "\u23f8 Pause Video", "fr": "\u23f8 Suspendre la Vidéo"},
    "media_play_audio": {"en": "\u25b6 Play Audio", "fr": "\u25b6 Lire l'Audio"},
    "media_pause_audio": {"en": "\u23f8 Pause Audio", "fr": "\u23f8 Suspendre l'Audio"},
    "no_quiz": {"en": "No quiz at this stop", "fr": "Aucun quiz à cet arrêt"},
    "quiz_available": {
        "en": "Quiz Available \u2014 Tap to Play!",
        "fr": "Quiz Disponible \u2014 Touchez pour Jouer !",
    },
    "quiz_completed": {"en": "Quiz completed for this stop", "fr": "Quiz terminé pour cet arrêt"},
    "take_photo": {"en": "Take Photo", "fr": "Prendre une Photo"},
    "share": {"en": "Share", "fr": "Partager"},
    "leave_comment": {"en": "Leave a comment...", "fr": "Laissez un commentaire..."},
    "post": {"en": "Post", "fr": "Publier"},
    "walk_to_a_stop": {"en": "Walk to a stop:", "fr": "Se rendre à un arrêt :"},
    "walk_to": {"en": "Walk to: ", "fr": "Se rendre à : "},
    "share_copied": {
        "en": "Share text copied to clipboard \u2014 paste it anywhere!",
        "fr": "Texte copié dans le presse-papiers \u2014 collez-le où vous voulez !",
    },
    "status_state": {"en": "State:", "fr": "État :"},
    "status_exploring": {"en": "exploring", "fr": "en exploration"},
    "status_points": {"en": "Points:", "fr": "Points :"},
    "status_visited": {"en": "Visited:", "fr": "Visités :"},
    "status_collectibles": {"en": "Collectibles:", "fr": "Objets à collectionner :"},
    "quit_quiz": {"en": "Quit Quiz", "fr": "Quitter le Quiz"},
    "correct": {"en": "\u2713 Correct!", "fr": "\u2713 Correct !"},
    "incorrect": {"en": "\u2717 Not quite.", "fr": "\u2717 Pas tout à fait."},
    "close": {"en": "Close", "fr": "Fermer"},
    "unlock_hint": {
        "en": "Answer every question correctly next time to unlock the collectible.",
        "fr": "Répondez correctement à toutes les questions la prochaine fois pour débloquer l'objet à collectionner.",
    },
    "quiz_time_title": {"en": "Quiz Time!", "fr": "C'est l'heure du Quiz !"},
    "question_of": {"en": "Question {i} of {n}", "fr": "Question {i} sur {n}"},
    "next_question": {"en": "Next Question", "fr": "Question Suivante"},
    "see_final_score": {"en": "See Final Score", "fr": "Voir le Score Final"},
    "wrong_prefix": {"en": "\u2717 Wrong. Correct answer:", "fr": "\u2717 Faux. Bonne réponse :"},
    "quiz_ended_early": {"en": "Quiz Ended Early", "fr": "Quiz Interrompu"},
    "quiz_complete": {"en": "Quiz Complete!", "fr": "Quiz Terminé !"},
    "score_label": {"en": "Score: {c} / {n} correct", "fr": "Score : {c} / {n} correctes"},
    "points_earned": {"en": "Points earned: {p}", "fr": "Points gagnés : {p}"},
    "collectible_unlocked": {"en": "Collectible unlocked: {name}!", "fr": "Objet débloqué : {name} !"},
    "share_via_title": {"en": "Share via...", "fr": "Partager via..."},
    "share_whatsapp": {"en": "WhatsApp", "fr": "WhatsApp"},
    "share_email": {"en": "Email", "fr": "Email"},
    "share_bluetooth": {"en": "Bluetooth", "fr": "Bluetooth"},
    "share_copy": {"en": "Copy to Clipboard", "fr": "Copier dans le Presse-papiers"},
    "share_cancel": {"en": "Cancel", "fr": "Annuler"},
    "share_bluetooth_unavailable": {
        "en": "Bluetooth file sharing isn't available on this device/OS. Copied the text instead \u2014 you can paste it into your Bluetooth app.",
        "fr": "Le partage par Bluetooth n'est pas disponible sur cet appareil. Le texte a été copié \u2014 vous pouvez le coller dans votre application Bluetooth.",
    },
    "share_bluetooth_opened": {
        "en": "Opened Bluetooth File Transfer \u2014 choose a device to send the exhibit text file to.",
        "fr": "Transfert de fichiers Bluetooth ouvert \u2014 choisissez un appareil pour envoyer le fichier.",
    },
    "share_whatsapp_opened": {
        "en": "Opening WhatsApp with your exhibit text ready to send...",
        "fr": "Ouverture de WhatsApp avec le texte de l'exposition prêt à envoyer...",
    },
    "share_email_opened": {
        "en": "Opening your email app with the exhibit text ready to send...",
        "fr": "Ouverture de votre application e-mail avec le texte prêt à envoyer...",
    },
    "view_comments": {"en": "\U0001f4ac Comments", "fr": "\U0001f4ac Commentaires"},
    "view_photos": {"en": "\U0001f5bc Gallery", "fr": "\U0001f5bc Galerie"},
    "comments_title": {"en": "Visitor Comments", "fr": "Commentaires des Visiteurs"},
    "photos_title": {"en": "Photos Taken", "fr": "Photos Prises"},
    "no_comments": {
        "en": "No comments yet \u2014 be the first to leave one!",
        "fr": "Aucun commentaire pour le moment \u2014 soyez le premier !",
    },
    "no_photos_taken": {
        "en": "You haven't taken any photos yet \u2014 tap Take Photo at a stop.",
        "fr": "Vous n'avez pas encore pris de photo \u2014 touchez Prendre une Photo à un arrêt.",
    },
    "photo_captured": {
        "en": "Photo captured! Find it in Gallery.",
        "fr": "Photo prise ! Retrouvez-la dans la Galerie.",
    },
    "comment_posted": {
        "en": "Comment posted on {stop}: {text}",
        "fr": "Commentaire publié sur {stop} : {text}",
    },
}


def tr(key: str, lang: str) -> str:
    """Look up a UI string by key for the given language, falling back
    to English if the language or key is missing."""
    entry = UI_STRINGS.get(key, {})
    return entry.get(lang) or entry.get("en") or key
