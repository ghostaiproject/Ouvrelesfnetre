"""Fun titles and jokes for the window alert, in English ("en") and French ("fr").
Pure functions, no network.

Lines are stored as text blocks, one "Title | Joke" per line (compact). A line
starting with "*" talks about sun: it is only used when it is actually sunny
right now (daytime and low cloud cover), so the joke always matches the sky.
Weather pools are picked from the current wind and temperature; close pools
from the reason (rain or cold). Every weather and close pool has 25 lines per language."""
import random
from datetime import date, timedelta

LANGS = ("en", "fr")


def _p(block):
    """'Title | Joke' lines -> [(title, joke, needs_sun)]."""
    out = []
    for line in block.strip().splitlines():
        sun = line.startswith("*")
        title, joke = line.lstrip("*").split("|", 1)
        out.append((title.strip(), joke.strip(), sun))
    return out


def _fixed(month, day):
    return lambda year: date(year, month, day)


def _thanksgiving(year):
    """Canadian Thanksgiving: second Monday of October."""
    d = date(year, 10, 1)
    first_monday = d + timedelta(days=(0 - d.weekday()) % 7)
    return first_monday + timedelta(days=7)


# name, date function, days the theme starts BEFORE, days it lasts AFTER
HOLIDAYS = [
    ("newyear", _fixed(1, 1), 2, 1),
    ("valentine", _fixed(2, 14), 2, 0),
    ("stpatrick", _fixed(3, 17), 1, 0),
    ("stjean", _fixed(6, 24), 2, 0),
    ("canadaday", _fixed(7, 1), 2, 0),
    ("thanksgiving", _thanksgiving, 2, 0),
    ("halloween", _fixed(10, 31), 7, 0),
    ("christmas", _fixed(12, 25), 13, 1),
    ("nye", _fixed(12, 31), 1, 0),
]

LINES = {"en": {k: _p(v) for k, v in {
    "newyear": """
New year, new pane | Fresh year, fresh air. Crack those windows.
Resolution, open up | Resolution number one: open the windows.
Cheers to fresh air | Pop the window, not just the bubbly.
New year's breeze | Start the year with a deep breath. Open up.
""", "valentine": """
Windows, my valentine | The fresh air has a crush on your apartment.
Pane-ing for you | Love is in the air. Literally. Let it in.
Be my vent-tine | Love at first breeze. Open up.
Sweet air-t | Give your home a little love. Open the windows.
""", "stpatrick": """
Luck of the pane | Lucky break. The air is perfect, no pot of gold needed.
Shamrock and roll | Rock some fresh air today.
Green light for windows | The air is lucky today. Open up.
""", "stjean": """
Saint-Jean pane party | Fete nationale vibes. Open up and let the fresh air in.
Pane-triotic breeze | Vive le Quebec. Good time to open up and enjoy the air.
Bonne fete, open up | Celebrate with fresh air.
Blue and white air | Quebec weather at its best. Open up.
""", "canadaday": """
Open up, eh | Perfect day for it. Very polite weather.
Pane-adian eh-ir | Happy Canada Day. Let the breeze in, sorry about the bugs.
Maple leaf breeze | Fresh air from sea to sea. Open up.
Eh-xcellent weather | Open up and celebrate.
""", "thanksgiving": """
Thankful for panes | Be thankful, the weather delivered. Windows open, leftovers cold.
Gobble up the breeze | Fresh air is the best side dish.
Thanks for the breeze | Grateful for good air. Open up.
Stuffing and fresh air | Open up before the food coma.
""", "halloween": """
Window of fright | The wind is whispering. Open a window, if you dare.
Pane-ic! Open up | Ghosts need ventilation too.
Boo-tiful breeze | Perfect weather for it. Just don't invite anything in.
Trick or breeze | Treat yourself to fresh air.
Ghoul-d weather | Good weather for ghouls and windows.
""", "christmas": """
Frosted panes | Santa checked the forecast. Windows open, you're good.
Sleigh the heat | Cool air is your free Christmas present.
Santa's window of opportunity | Open up before the elves get cold.
Ho ho open | Ho ho ho, open the window.
Jingle all the air | Fresh air all the way.
""", "nye": """
Last pane of the year | End the year with fresh air.
Out with the old air | Out with the old air, in with the new.
Year-end breeze | Close the year with an open window.
"""}.items()}, "fr": {k: _p(v) for k, v in {
    "newyear": """
Nouvelle année, nouvel air | Année neuve, air neuf. Ouvre les fenêtres.
Résolution : aérer | Résolution numéro un : ouvrir les fenêtres.
Santé à l'air frais | Ouvre la fenêtre, pas juste le mousseux.
Brise du jour de l'an | Commence l'année avec une bonne respiration.
""", "valentine": """
Coup de foudre pour l'air | L'air frais a un kick sur ta maison.
L'amour est dans l'air | Littéralement. Laisse-le entrer.
Mon cœur bat pour l'air | Ouvre les fenêtres, par amour.
Douce brise d'amour | Donne un peu d'amour à ta maison. Ouvre.
""", "stpatrick": """
Chanceux de la vitre | Pas besoin de trèfle, l'air est parfait.
Trèfle et courant d'air | L'air est chanceux aujourd'hui. Ouvre.
Feu vert pour aérer | Ouvre les fenêtres.
""", "stjean": """
Bonne Saint-Jean | Bonne fête nationale! Ouvre et laisse entrer l'air.
Vive l'air du Québec | Fête nationale : c'est le temps d'ouvrir les fenêtres.
Air bleu et blanc | Temps québécois à son meilleur. Ouvre.
Fête de l'air frais | Fête nationale, fenêtres ouvertes.
""", "canadaday": """
Bonne fête du Canada | Temps parfait. Ouvre les fenêtres.
Air canadien, eh | Laisse entrer la brise. Désolé pour les maringouins.
Brise d'érable | Air frais d'un océan à l'autre. Ouvre.
Bonne fête, eh | Ouvre et célèbre.
""", "thanksgiving": """
Merci la météo | Action de grâce : l'air est parfait. Ouvre.
Dinde et courant d'air | L'air frais, le meilleur accompagnement.
Merci pour la brise | Reconnaissant pour le bon air. Ouvre.
Farce et air frais | Ouvre avant le coma de dinde.
""", "halloween": """
Fenêtre de l'effroi | Le vent murmure. Ouvre une fenêtre, si tu l'oses.
Les fantômes aussi aèrent | Ouvre les fenêtres. Bouh!
Air à faire peur | Temps parfait. N'invite juste rien d'étrange.
Un bonbon ou de l'air | L'air frais, c'est la meilleure gâterie.
Temps de sorcière | Bon temps pour les sorcières et les fenêtres.
""", "christmas": """
Vitres givrées? Non! | Le père Noël a vérifié la météo. Ouvre.
Cadeau d'air frais | L'air frais, ton cadeau de Noël gratuit.
Lutins en manque d'air | Ouvre avant que les lutins aient froid.
Ho ho, ouvre | Ho ho ho, ouvre la fenêtre.
Vive le vent | Vive le vent qui entre par la fenêtre.
""", "nye": """
Dernière fenêtre de l'année | Termine l'année au grand air.
Dehors le vieil air | Dehors le vieil air, place au neuf.
Brise de fin d'année | Termine l'année avec une fenêtre ouverte.
"""}.items()}}

# Picked by the weather outside. {deg} becomes the current temp ("19°" or "19 degrees").
# breezy = wind 20 km/h or more, cool = under 18, mild = 18 to 20, warm = over 20.
WEATHER_LINES = {"en": {k: _p(v) for k, v in {
    "breezy": """
Breezy {deg}, wind-ow time | A wind-ow of fresh air awaits. Hold on to your papers.
{deg} and gust-o | Good gusts out there. Breeze through it and open up.
Hinge-credible {deg} breeze | Hinge-credible air is blowing outside.
Gone with the wind-ow, {deg} | Frankly, my dear, the air is perfect. Open up.
{deg}, blowout sale on air | Fresh air for zero dollars. Limited time, open now.
Breeze-y does it, {deg} | Easy does it. Slide that window and let the wind work.
{deg} and a draft pick | Your team just drafted a breeze. Put it in the lineup.
Whirl-d class {deg} | World class breeze outside. Front row seats by the window.
{deg}, air mail delivery | The wind has a package for you. Open the window to sign for it.
Sash-tastic {deg} breeze | The breeze is sash-tastic today. Open up.
{deg}, fan service | Nature turned on the big fan. Free of charge.
Draft day, {deg} | Good draft outside. The healthy kind.
{deg} and blowing up | The breeze is trending. Let it go viral in your living room.
Pane-oramic {deg} breeze | Big breeze, big view. Open wide.
Latch on to {deg} | Unlatch the window and let the breeze latch on.
Gust in time, {deg} | Gust in time to open up. Don't blow it.
{deg}, the air is up | The breeze is up and running. Let it in.
Blown away by {deg} | You'll be blown away. Open the windows.
{deg}, knock knock | Hear that? The breeze is knocking. Open up.
Air we go, {deg} | Air we go! Open the windows.
{deg}, a real blowhard | The wind won't stop talking. Let it in anyway.
{deg}, tail wind | Ride the tail wind. Open up.
Second wind, {deg} | Your place needs a second wind. Open the windows.
{deg}, flutter by | The curtains want to dance. Give them a breeze.
{deg}, kite weather | Kite weather outside. Window weather inside.
""", "cool": """
Crisp {deg}, crack a pane | Crack it open. Crack a smile. Crack a pane joke.
Cool {deg}, sill waiting | Why sit around being sill-y? Let the cool air in.
{deg} of chill-ax air | Not cold, just chill. Unlatch it and let it in.
{deg}, cool beans, open panes | Cool beans. Even cooler air. Open up.
Fresh {deg}, mint condition | Air in mint condition. Unwrap it.
{deg}, sweater weather | Grab a sweater and let the fresh air in.
Brisk {deg} business | Business is brisk out there. Open for business.
{deg}, ice to meet you | Not ice cold, just nice cold. Open up.
Cool {deg}, frame it | Air this fresh deserves a frame. A window frame.
{deg}, keep your cool | Stay cool, and let the cool in.
Crisp {deg}, apple air | Crisp like an apple. Take a bite of fresh air.
{deg}, refresh button | Your place needs a refresh. The window is the button.
Cool {deg}, glass act | A real glass act of weather. Open up.
{deg}, air you ready? | Air you ready for fresh air? Open up.
Fresh {deg} delivery | Fresh air, delivered cool. No tip needed.
{deg}, a cool million | A cool million breaths of fresh air. Open up.
Chilled {deg}, served fresh | Fresh air, served chilled. Open the window.
{deg}, sill chilling | The sill is chilling. Join it. Open up.
Nippy {deg} | A little nippy, a lot fresh. Open up.
{deg}, cool runnings | Let the cool air run through. Open up.
{deg}, nature's AC | Nature's air conditioner is on. Open up.
{deg}, fresh not frosty | Fresh but not frosty. Open the windows.
Cool {deg}, slide in | Slide the window, slide in the fresh air.
{deg}, extra crispy | Fresh air, extra crispy. Open up.
{deg}, too cool for school | Too cool for school, just right for windows.
""", "mild": """
{deg} of pane relief | Open up and feel the glass-ful of fresh air.
Window of opportunity at {deg} | Don't let this one slide. Windows slide, get it?
Goldilocks {deg} | Not too hot, not too cold. Frame-worthy air.
{deg}, open and shut case | The case for fresh air is wide open.
{deg}, pane-fect | This is pane-fect weather. Open up.
{deg}, sill-ky smooth | Smooth air, silky breeze. Open the windows.
{deg}, open season | Open season on fresh air. No license needed.
{deg}, no pane no gain | No pane, no gain. Open up and gain fresh air.
Mild {deg}, wild idea | Wild idea: open the windows.
{deg}, breath of fresh pane | Take a breath. Then take a window.
{deg}, sash-sational | Sash-sational weather. Slide it open.
{deg}, crack-ing good | Crack-ing good air out there. Crack one open.
{deg}, room to breathe | Give your room some room to breathe.
{deg}, air-resistible | Air-resistible weather. Don't resist, open up.
Frame-ous {deg} | Frame-ous last words: should have opened the window.
{deg}, pane and simple | Pane and simple: open the windows.
{deg}, sweet spot | The weather hit the sweet spot. Open up.
{deg}, mild-ly amazing | Mildly amazing air. Open the windows.
{deg}, frame of mind | Get in the right frame of mind. Open up.
{deg}, latch-ly perfect | Unlatch and enjoy. It's perfect out.
{deg}, clear as glass | It's clear as glass: open the windows.
{deg}, just breathe | Open the windows and just breathe.
{deg}, comfy cozy | Comfy outside, cozy inside. Let them mix.
{deg}, fresh start | Fresh air, fresh start. Open up.
{deg}, by the book | Textbook weather. Open up.
""", "warm": """
Warm {deg}, glass half open | The optimist's way to cool the place.
Ledge-endary {deg} | Today's warm breeze is ledge-endary. Open up.
{deg}, don't pane | It's easy. Just sash-ay on over to the window.
{deg}, heated debate over | Debate over. Windows open.
Toasty {deg}, butter up | Warm as toast. Spread the fresh air around.
*{deg}, sunny side up | Sunny side up, windows up.
{deg}, hot take: open up | Hot take: the window should be open.
{deg}, warm welcome | Give the breeze a warm welcome.
{deg}, summer-ize it | Summer-ize your living room. Open up.
{deg}, sill-y warm | Sill-y warm outside. Let it flow.
{deg}, beach pane | No beach, but the breeze is close enough.
*Golden {deg} | Golden sun out there. Let it shine in.
*{deg}, made in the shade | You've got it made in the shade. Open the windows.
{deg}, cool it down | Warm in here? Let the breeze cool it down.
{deg}, open-air concert | The birds are playing. Open up for the show.
*{deg}, sun's out, panes out | Sun's out, windows out. Open up.
{deg}, cooking with air | Let the breeze in before the oven gets jealous.
{deg}, warm fuzzies | Warm fuzzy weather. Open up.
{deg}, patio mode | Patio mode activated. Open the windows.
*{deg}, glow up | The sun is glowing. Let it in.
{deg}, flip-flop weather | Flip-flop weather. Flip the latch.
{deg}, summer feels | Summer feels outside. Share them inside.
{deg}, air flow show | Get the air flowing. Open two windows across from each other.
{deg}, warmed up and ready | The weather's warmed up. Open up.
{deg}, toasty and breezy | Toasty out, stuffy in. Fix that. Open up.
"""}.items()}, "fr": {k: _p(v) for k, v in {
    "breezy": """
{deg} et ça vente | Belle brise dehors. Ouvre et laisse entrer l'air.
Courant d'air de luxe, {deg} | Un courant d'air cinq étoiles. Ouvre les fenêtres.
{deg}, vent de fraîcheur | Un vent de fraîcheur souffle. Laisse-le entrer.
Ça souffle à {deg} | Tiens tes papiers et ouvre les fenêtres.
{deg}, le vent tourne | Le vent tourne en ta faveur. Ouvre.
Brise de {deg} | Brise la glace : ouvre une fenêtre.
{deg}, ventilation gratuite | La nature fait le ménage de l'air. Gratis.
{deg}, coup de vent | Passe en coup de vent ouvrir les fenêtres.
{deg}, l'air de rien | L'air de rien, c'est parfait dehors. Ouvre.
Vitre ouverte, {deg} | Le vent cogne à la vitre. Laisse-le entrer.
{deg}, gros ventilo | La nature a parti son gros ventilo.
{deg}, ça décoiffe | Une brise qui décoiffe. Ouvre pareil.
{deg}, coup de cœur | Une brise qui fait du bien. Ouvre les fenêtres.
{deg}, air de fête | Le vent a un air de fête. Invite-le.
{deg}, à tout vent | Ouvre à tout vent, c'est le moment.
{deg}, vent dans les voiles | T'as le vent dans les voiles. Ouvre.
{deg}, rideaux qui dansent | Les rideaux veulent danser. Ouvre.
{deg}, souffle de vie | Un bon souffle d'air t'attend.
{deg}, ça brasse | Ça brasse dehors, juste assez. Ouvre.
{deg}, temps de cerf-volant | Cerf-volant dehors, fenêtre ouverte en dedans.
{deg}, la brise du jour | La brise du jour est servie. Ouvre.
{deg}, second souffle | Ta maison a besoin d'un second souffle. Ouvre.
{deg}, vent du large | Un petit vent du large. Ouvre les fenêtres.
{deg}, air en livraison | Le vent a un colis pour toi. Ouvre pour signer.
{deg}, coup de balai | Le vent fait le ménage. Ouvre.
""", "cool": """
{deg}, fraîcheur garantie | Air frais livré à ta fenêtre. Ouvre.
Frisquet à {deg} | Pas froid, juste frisquet. Ouvre un peu.
{deg}, tête froide | Garde la tête froide, laisse entrer le frais.
{deg}, petite laine | Mets une petite laine et ouvre les fenêtres.
{deg}, frais comme une vitre | Aussi frais qu'une vitre le matin. Ouvre.
{deg}, au frais | Mets la maison au frais. Ouvre.
Croquant à {deg} | L'air est frais comme une pomme. Croque dedans.
{deg}, on aère | Allez, on aère. Ta maison va te remercier.
{deg}, bouffée d'air | Une bonne bouffée d'air frais t'attend.
{deg}, un carreau de frais | Ouvre un carreau, fais entrer le frais.
{deg}, ça rafraîchit | Appuie sur rafraîchir : ouvre la fenêtre.
{deg}, cool en titi | Cool en titi dehors. Ouvre.
{deg}, frais et dispo | L'air est frais et dispo. Toi aussi?
{deg}, air de chalet | Un air de chalet en ville. Ouvre.
{deg}, fraîcheur maison | Fraîcheur maison, servie à la fenêtre.
{deg}, frais comme une rose | L'air est frais comme une rose. Ouvre.
{deg}, clim naturelle | La clim naturelle est partie. Ouvre.
{deg}, frisquet mais correct | Correct pour aérer. Ouvre un peu.
{deg}, fraîcheur à volonté | Ouvre et fais entrer la fraîcheur.
{deg}, coton ouaté | Mets ton coton ouaté, ouvre les fenêtres.
{deg}, frais pas glacé | Pas glacé, juste frais. Ouvre.
{deg}, croustillant | L'air est croustillant. Ouvre.
{deg}, air pur | De l'air pur à volonté. Ouvre.
{deg}, du frais en masse | Du frais en masse dehors. Ouvre.
{deg}, cool Raoul | Cool Raoul. Ouvre les fenêtres.
""", "mild": """
{deg}, tout en douceur | Ouvre tout en douceur. L'air est parfait.
{deg}, ni trop ni pas assez | Boucle d'or approuve. Ouvre les fenêtres.
{deg}, fenêtre d'opportunité | Une vraie fenêtre d'opportunité. Ouvre-la.
{deg}, doux comme un minou | Air doux comme un minou. Ouvre.
{deg}, vitre-ment parfait | C'est vitre-ment parfait dehors. Ouvre.
{deg}, on ouvre le bal | Ouvre le bal, ouvre les fenêtres.
{deg}, à bras ouverts | Accueille l'air à bras et à fenêtres ouverts.
{deg}, air de printemps | Ça sent bon dehors. Fais entrer ça.
{deg}, la belle affaire | Air frais à zéro piasse. Profites-en.
{deg}, ouvert pour affaires | Les fenêtres sont ouvertes pour affaires.
{deg}, respire par le nez | Respire par le nez et ouvre les fenêtres.
{deg}, c'est dans l'air | Le beau temps est dans l'air. Laisse-le entrer.
{deg}, on s'aère l'esprit | Aère la maison, aère l'esprit.
{deg}, parfait de même | Touche à rien, sauf aux fenêtres.
{deg}, cadre parfait | Un air digne d'un cadre. De fenêtre.
{deg}, pile poil | Pile poil la bonne température. Ouvre.
{deg}, le bon moment | C'est le bon moment. Ouvre les fenêtres.
{deg}, la douceur même | La douceur même dehors. Ouvre.
{deg}, bonne nouvelle | Bonne nouvelle : c'est parfait pour aérer.
{deg}, clair comme une vitre | C'est clair : ouvre les fenêtres.
{deg}, comme un charme | Ça marche comme un charme dehors. Ouvre.
{deg}, juste milieu | La météo a trouvé le juste milieu. Ouvre.
{deg}, nouveau départ | Air neuf, nouveau départ. Ouvre.
{deg}, c'est un signe | Cette météo est un signe. Ouvre.
{deg}, dans le mille | La météo frappe dans le mille. Ouvre.
""", "warm": """
{deg}, chaud devant | Chaud devant! Ouvre pour faire circuler l'air.
{deg}, ça chauffe | Ça chauffe un peu. Laisse entrer la brise.
*{deg}, soleil en vitrine | Le soleil fait de la vitrine. Ouvre.
{deg}, chaud mais aéré | Garde ça chaud, mais aéré. Ouvre.
{deg}, beau temps, bon vent | Beau temps, bon vent. Ouvre les fenêtres.
{deg}, air d'été | Un petit air d'été. Fais-le entrer.
{deg}, terrasse à domicile | Ouvre les fenêtres, voilà ta terrasse.
{deg}, on fait de l'air | Fais de l'air dans la maison.
{deg}, chaleur humaine | Accueille la chaleur, fais circuler l'air.
*{deg}, le soleil cogne | Le soleil cogne à la vitre. Ouvre-lui.
*{deg}, vitres au soleil | Ouvre et profite du soleil.
{deg}, ouvre la cage | Libère l'air chaud, fais entrer la brise.
*{deg}, rayon de soleil | Un rayon de soleil t'attend à la fenêtre.
{deg}, ça sent l'été | Ça sent l'été dehors. Ouvre.
{deg}, mode terrasse | Mode terrasse activé. Ouvre.
{deg}, ça réchauffe | Ça réchauffe! Fais circuler l'air.
*{deg}, petit soleil | Un petit soleil t'attend. Ouvre.
{deg}, temps de gougounes | Temps de gougounes. Ouvre le loquet.
{deg}, ça mijote | Ça mijote dehors. Fais de l'air en dedans.
{deg}, l'été s'invite | L'été s'invite. Ouvre-lui.
*{deg}, ça brille | Le soleil brille. Laisse-le entrer.
{deg}, courant d'air d'été | Ouvre deux fenêtres face à face pour un beau courant d'air.
{deg}, chaud et doux | Chaud et doux dehors. Ouvre.
{deg}, belle journée | Belle journée! Ouvre les fenêtres.
{deg}, maison étouffante? | Pas pour longtemps. Ouvre.
"""}.items()}}

CLOSE_LINES = {"en": {k: _p(v) for k, v in {
    "rain": """
Pane in the forecast | Rain is on the way. Close the windows!
Rain check on that breeze | Rain incoming. Shut the windows.
Don't rain on your own parade | Close the windows before it pours.
No pane-ic, just close up | Rain is coming. Calmly close the windows.
Wet forecast, shut case | Rain is on its way. Close the windows.
Drip drop, window stop | Rain soon. Time to shut the windows.
Sill-y to leave it open | Rain is coming. It'd be sill-y to leave the windows open.
Puddle trouble | Close the windows before the sill becomes a pool.
Umbrella not included | Your windows don't have one. Close them.
Rain-dow alert | Rain is near. Close the windows.
Shut the pane door | Rain incoming. Shut it all.
Showers expected, not inside | Close the windows. Keep the showers outside.
The sky is leaking | Rain soon. Close the windows to stay dry.
Splash zone ahead | Close the windows. Your floor didn't buy a ticket.
Weather or not, close up | Rain is coming. Close the windows.
Rain, rain, go away | And stay outside. Close the windows.
Sill pool party cancelled | Close the windows before the rain.
Drop it like it's closed | Rain is coming. Close the windows.
Clouds are crying | Rain soon. Close the windows.
Indoor rain not included | Close the windows.
Free window wash incoming | Keep it outside. Close up.
Forecast: soggy | Close the windows before the rain.
Hold the water | Rain coming. Shut the windows.
Pitter patter, close the latter | Rain soon. Close the windows.
Gray skies, shut eyes | Rain is coming. Shut the windows.
""", "cold": """
Pane-ful chill | It's getting cold out. Close the windows.
Chill out, close up | The temperature is dropping. Time to shut the windows.
Cold front, hold the pane | Close the windows to keep the warmth in.
Brrr-eak time is over | It's getting cold. Close the windows.
Frost-ration ahead | The cold is coming. Shut the windows.
Cold shoulder from outside | The air turned cold. Close up.
Chilly willy | The temperature is dropping. Close the windows.
Ice ice, maybe | Getting cold out. Close the windows.
Keep the heat in | It's cooling off. Shut the windows to stay warm.
Window of warmth closing | The nice air is over. Close up.
Freeze, close up | It's getting cold. Close the windows.
Cool story, close it | The air is getting cold. Shut the windows.
Sweater won't cut it | Getting cold. Close the windows.
Pane and simple: close | The temperature is dropping. Close up.
Draft dodger | Cold air coming. Dodge the draft, close the windows.
Cold call | The cold is calling. Close the windows.
Shiver me windows | It's getting cold. Close up.
Cool it, close it | The temperature is dropping. Close the windows.
Brr-illiant idea: close up | It's getting cold. Close the windows.
Chill pill | Cold is coming. Close the windows.
Cold feet | Don't get cold feet. Close the windows.
Warmth patrol | Close the windows to keep the heat in.
Fridge mode off | Getting cold. Close up.
Frosty forecast | The cold is coming. Shut the windows.
Heat is precious | It's cooling down. Close the windows.
"""}.items()}, "fr": {k: _p(v) for k, v in {
    "rain": """
Pluie en vue | La pluie s'en vient. Ferme les fenêtres!
Ferme, ça va mouiller | Pluie bientôt. Ferme tout.
Alerte à la flaque | Ferme avant que le rebord devienne une piscine.
Il va pleuvoir des clous | Ou juste de la pluie. Ferme quand même.
Parapluie pas inclus | Tes fenêtres n'en ont pas. Ferme-les.
Goutte à goutte, on ferme | La pluie arrive. Ferme les fenêtres.
Douche prévue, pas en dedans | Garde la pluie dehors. Ferme.
Le ciel coule | Pluie bientôt. Ferme les fenêtres.
Mouillé? Non merci | La pluie approche. Ferme tout.
Vitres fermées, plancher sec | La pluie arrive. Ferme les fenêtres.
Pas de bain intérieur | Ferme les fenêtres, la pluie s'en vient.
Ça va tomber | De la pluie bientôt. Ferme.
Nuages menaçants | Ferme les fenêtres avant l'averse.
Averse en approche | Ferme les fenêtres, vite.
Pluie au menu | Ferme les fenêtres avant le service.
Pluie, pluie, va-t'en | Et reste dehors. Ferme les fenêtres.
Lavage de vitres gratuit | Dehors seulement. Ferme.
Météo : détrempée | Ferme les fenêtres avant la pluie.
Les nuages pleurent | Pluie bientôt. Ferme les fenêtres.
Gare aux gouttes | La pluie arrive. Ferme.
Rebord inondé? Non | Ferme les fenêtres avant la pluie.
Pas de piscine intérieure | Ferme les fenêtres, ça s'en vient.
Ploc ploc | La pluie approche. Ferme les fenêtres.
Temps de canard | Pluie en route. Ferme.
Ciel gris, fenêtres fermées | La pluie arrive. Ferme.
""", "cold": """
Ça se refroidit | Il commence à faire froid. Ferme les fenêtres.
Brrr, on ferme | La température baisse. Ferme tout.
Garde ta chaleur | Ferme les fenêtres pour garder le chaud.
Froid en vue | Le froid s'en vient. Ferme.
Fin de la pause fraîcheur | C'est fini pour aujourd'hui. Ferme.
Frette en approche | Ça devient frette. Ferme les fenêtres.
On ferme boutique | Le froid arrive. Ferme les fenêtres.
Courant d'air glacé | Ferme avant que ça gèle.
Fenêtre d'opportunité fermée | Le beau moment est passé. Ferme.
Pas besoin d'un frigo géant | Ferme les fenêtres, ça refroidit.
Froid de canard | Bon, pas tant que ça. Ferme quand même.
Fini la fraîcheur | Il fait trop frais. Ferme.
Chaleur à garder | Ferme les fenêtres pour rester au chaud.
Le thermomètre descend | Ferme les fenêtres.
Sors ta tuque | Ou ferme les fenêtres. C'est plus simple.
Ça pince | Il commence à pincer. Ferme les fenêtres.
Frisson en vue | Le froid arrive. Ferme.
Mode frigo désactivé | Ça refroidit. Ferme les fenêtres.
Pas de pieds gelés | Ferme les fenêtres avant d'avoir froid.
On garde le chaud | Ferme les fenêtres.
Bise glaciale | La bise arrive. Ferme.
Le coton ouaté suffit plus | Ça refroidit. Ferme les fenêtres.
Thermostat en danger | Ferme les fenêtres pour sauver le chauffage.
Fin de la récré | Il fait trop froid. Ferme.
Ça descend vite | La température baisse. Ferme les fenêtres.
"""}.items()}}

# Units and the weather line, per language. Same words on screen and in speech.
WORDS = {
    "en": {"deg": "degrees", "unit": "C",
           "stats": "{t} {u} outside, {h} percent humidity, dew point {d}."},
    "fr": {"deg": "degrés", "unit": "C",
           "stats": "{t} {u} dehors, {h} pour cent d'humidité, point de rosée {d}."},
}


def norm_lang(lang) -> str:
    return lang if lang in LANGS else "en"


def holiday_for(d: date):
    for name, fn, before, after in HOLIDAYS:
        for year in (d.year - 1, d.year, d.year + 1):
            delta = (fn(year) - d).days
            if -after <= delta <= before:
                return name
    return None


def weather_kind(w: dict) -> str:
    """breezy, cool, mild or warm: picks which WEATHER_LINES pool to use."""
    if w["wind"] >= 20:
        return "breezy"
    if w["temp"] < 18:
        return "cool"
    if w["temp"] <= 20:
        return "mild"
    return "warm"


def _pick(rng, lines, sunny):
    """Random line that fits the sky right now: sun lines only when sunny."""
    ok = [x for x in lines if sunny or not x[2]]
    title, joke, _ = rng.choice(ok)
    return title, joke


def build_message(d: date, w: dict, spoken: bool = False, rng=random, close=None, lang="en"):
    """Return (title, body) in `lang` ("en" or "fr"). Themed lines near a holiday,
    otherwise one matching the current weather. Open titles always carry the current temp."""
    lang = norm_lang(lang)
    words, sunny = WORDS[lang], bool(w.get("sunny"))
    if close:
        pools = CLOSE_LINES[lang]
        return _pick(rng, pools.get(close) or pools["cold"], sunny)
    temp = f"{w['temp']:.0f}"
    deg = f"{temp} {words['deg']}" if spoken else f"{temp}°"
    holiday = LINES[lang].get(holiday_for(d))
    if holiday:
        title, joke = _pick(rng, holiday, sunny)
        title = f"{title}, {deg}"
    else:
        title, joke = _pick(rng, WEATHER_LINES[lang][weather_kind(w)], sunny)
        title = title.format(deg=deg)
    stats = words["stats"].format(t=temp, u=words["deg"] if spoken else words["unit"],
                                  h=f"{w['humidity']:.0f}", d=f"{w['dew_point']:.0f}")
    return title, f"{joke} {stats}"


# ------------------------------------------------ "should I open?" answer ---
# Why not, per failed check (alert.py evaluate). {t} temp, {h} humidity, {d} dew
# point, {w} wind km/h, {m} lowest temp in the next 2h. Spoken text.
REASONS = {
    "en": {
        "too_cold": "it's only {t} degrees, too cool", "too_hot": "it's {t} degrees, too warm",
        "too_damp": "humidity is {h} percent, too damp", "too_dry": "the air is too dry, {h} percent humidity",
        "dew_point": "it's muggy, dew point {d}", "no_precip": "it's raining right now",
        "no_rain_soon": "rain is coming in the next 2 hours",
        "not_getting_cold": "it's dropping to {m} degrees soon", "wind": "it's too windy, {w} kilometres an hour",
        "no": "Not right now: {why}.", "and": " and ",
        "yes": "Yes! {title}. {body}", "error": "Sorry, I can't get the weather right now. Try again in a minute.",
        "help": "Ask me: should I open the windows?", "bye": "Bye!",
    },
    "fr": {
        "too_cold": "il fait juste {t} degrés, trop frais", "too_hot": "il fait {t} degrés, trop chaud",
        "too_damp": "l'humidité est à {h} pour cent, trop humide", "too_dry": "l'air est trop sec, {h} pour cent d'humidité",
        "dew_point": "c'est collant, point de rosée {d}", "no_precip": "il pleut en ce moment",
        "no_rain_soon": "de la pluie s'en vient dans les 2 prochaines heures",
        "not_getting_cold": "ça descend à {m} degrés bientôt", "wind": "il vente trop, {w} kilomètres à l'heure",
        "no": "Pas maintenant : {why}.", "and": " et ",
        "yes": "Oui! {title}. {body}", "error": "Désolé, je n'arrive pas à avoir la météo. Réessaie dans une minute.",
        "help": "Demande-moi : est-ce que j'ouvre les fenêtres?", "bye": "Bye!",
    },
}
