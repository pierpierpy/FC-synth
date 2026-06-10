"""
FC Dataset Prompt Builder

Builds the teacher prompts used to generate multi-turn function-calling
conversations. The block dictionaries below contain the (intentionally
bilingual IT/EN) prompt text that instructs the teacher model how to produce
the dataset; only the Python docstrings and comments in this module are in
English.
"""

import random
from typing import Dict, List, Optional, Any
import json


# =============================================================================
# CALL TYPE + SUBTYPE BLOCKS (11 blocks)
# =============================================================================

CALL_TYPE_BLOCKS = {
    # POSITIVE
    ("positive", "direct"): [
        """L'utente fa una richiesta chiara che richiede l'uso di un tool.
L'assistant DEVE chiamare il tool appropriato IMMEDIATAMENTE, senza convenevoli.""",
        
        """L'utente chiede qualcosa di specifico che necessita un tool.
L'assistant risponde chiamando subito il tool corretto.""",
        
        """Richiesta diretta dell'utente → l'assistant chiama il tool giusto senza esitazioni.
Niente chiacchiere, azione immediata."""
    ],
    
    ("positive", "after_chitchat"): [
        """La conversazione inizia con chit-chat (saluti, convenevoli, come stai).
Dopo alcuni scambi informali, l'utente fa una richiesta che richiede un tool.
L'assistant DEVE chiamare il tool quando l'utente fa la richiesta specifica.""",
        
        """Prima c'è una fase di convenevoli e chiacchiere leggere.
Poi l'utente arriva al punto e chiede qualcosa che richiede un tool.
L'assistant riconosce la richiesta e chiama il tool appropriato.""",
        
        """Conversazione che parte informale (saluti, domande generiche).
A un certo punto l'utente fa una richiesta concreta → tool call."""
    ],
    
    ("positive", "followup"): [
        """L'utente fa una prima richiesta → l'assistant chiama un tool e mostra il risultato.
Poi l'utente chiede qualcosa di correlato o vuole approfondire.
L'assistant chiama un altro tool per soddisfare la nuova richiesta.""",
        
        """Sequenza di tool call: primo tool → risultato → l'utente vuole di più → secondo tool.
Ogni tool call è motivato da una richiesta esplicita dell'utente.""",
        
        """Conversazione con più tool call in sequenza.
L'utente ottiene un risultato, poi chiede qualcosa di collegato che richiede un altro tool."""
    ],
    
    ("positive", "multi_tool"): [
        """L'utente fa una richiesta complessa che richiede l'uso di PIÙ TOOL.
L'assistant può chiamare più tool in sequenza o riconoscere che servono più passaggi.
Ogni tool call deve essere giustificato dalla richiesta.""",
        
        """Richiesta articolata che non si risolve con un singolo tool.
L'assistant deve orchestrare 2 o più tool per soddisfare completamente l'utente.""",
        
        """L'utente ha bisogno di qualcosa che richiede più operazioni.
L'assistant chiama i tool necessari, uno dopo l'altro, spiegando il processo."""
    ],
    
    ("positive", "after_clarification"): [
        """L'utente fa una richiesta inizialmente VAGA o incompleta.
L'assistant chiede chiarimenti per capire meglio cosa serve.
L'utente fornisce le informazioni mancanti → l'assistant chiama il tool.""",
        
        """Prima richiesta poco chiara → l'assistant chiede dettagli.
L'utente chiarisce → ora l'assistant ha abbastanza info per chiamare il tool.""",
        
        """Richiesta ambigua iniziale. L'assistant non inventa ma chiede.
Dopo il chiarimento dell'utente, procede con il tool call appropriato."""
    ],
    
    # NEGATIVE
    ("negative", "no_need"): [
        """Scenario di conversazione informale.
L'utente vuole solo chiacchierare, chiedere un'opinione o parlare del più e del meno.
Esempio: "Ciao, come stai?" oppure "Cosa ne pensi del tempo oggi?" oppure "Mi dai un consiglio su..."
L'assistant risponde in modo cordiale e conversazionale, come un assistente amichevole.""",
        
        """L'utente ha una domanda di cultura generale o vuole un parere.
Esempi: "Qual è la capitale della Francia?", "Mi consigli un buon libro?", "Come si dice grazie in spagnolo?"
L'assistant risponde direttamente con le sue conoscenze, in modo naturale e utile.""",
        
        """Conversazione sociale: l'utente saluta, ringrazia, o fa small talk.
Esempi tipici: "Buongiorno!", "Grazie mille per l'aiuto!", "A dopo!", "Come funziona questo servizio?"
L'assistant è cortese e risponde appropriatamente al contesto sociale."""
    ],
    
    ("negative", "out_of_scope"): [
        """L'utente chiede qualcosa che NESSUNO dei tool disponibili può fare.
L'assistant spiega gentilmente che non può aiutare con quella richiesta specifica.
NON inventa capacità che non ha, NON chiama tool a caso.""",
        
        """Richiesta fuori dalla portata dei tool disponibili.
L'assistant deve riconoscerlo e comunicarlo chiaramente all'utente.
Può suggerire alternative o chiedere se può aiutare in altro modo.""",
        
        """L'utente vuole qualcosa che i tool presenti non supportano.
L'assistant è onesto: spiega cosa può e cosa non può fare."""
    ],
    
    ("negative", "already_answered"): [
        """Conversazione semplice: l'utente fa una domanda di cultura generale.
Esempio reale: "Ciao! Quanti giorni ha febbraio?" → L'assistant risponde: "28 giorni, 29 negli anni bisestili!"
Oppure: "Sai dirmi qual è la capitale dell'Italia?" → "Certamente, è Roma!"
Dialogo naturale e cordiale.""",
        
        """L'utente chiede qualcosa che sa già l'assistant.
Esempi: "Come si dice 'grazie' in inglese?" "Quanto fa 7x8?" "Qual è il prefisso telefonico italiano?"
L'assistant risponde in modo amichevole e immediato.""",
        
        """Domanda semplice con risposta diretta.
Tipo: "Mi ricordi l'orario di apertura delle banche?" o "Quanti minuti ci sono in un'ora?"
L'assistant risponde cordialmente."""
    ],
    
    # CLARIFICATION
    ("clarification", "resolved"): [
        """L'utente fa una richiesta VAGA o AMBIGUA.
L'assistant chiede chiarimenti specifici (quale documento? che periodo? etc.).
L'utente risponde con informazioni SUFFICIENTI.
L'assistant CHIAMA il tool con le informazioni ottenute.""",
        
        """Richiesta iniziale poco chiara → domanda di chiarimento → risposta utente → tool call.
Il chiarimento RISOLVE l'ambiguità e permette di procedere.""",
        
        """L'utente non è preciso all'inizio. L'assistant chiede cosa manca.
Una volta ottenute le info necessarie, l'assistant procede con il tool."""
    ],
    
    ("clarification", "unresolved"): [
        """L'utente fa una richiesta ma mancano dettagli importanti.
L'assistant chiede gentilmente di specificare (es: "Quale mese intendi?" "Per quale servizio?").
L'utente però non riesce a fornire le informazioni richieste, magari cambia argomento o resta generico.
La conversazione si conclude senza che l'assistant abbia i dati necessari per procedere.""",
        
        """Scenario dove l'utente è confuso o indeciso.
L'assistant cerca di aiutare chiedendo chiarimenti, ma l'utente non ha le informazioni o non sa cosa vuole.
Esempio: "Vorrei fare quella cosa..." - "Quale cosa intendi?" - "Boh, non so, lascia stare."
Conversazione che finisce con l'utente che rinuncia o rimanda.""",
        
        """L'utente inizia una richiesta ma poi si rende conto di non avere i dettagli necessari.
L'assistant è paziente e chiede cosa serve, ma l'utente non può fornirlo.
Esempio tipico: "Voglio controllare... ah no aspetta, non ho il codice con me, riprovo dopo."
"""
    ],
    
    ("clarification", "partial"): [
        """L'utente fa una richiesta VAGA.
L'assistant chiede chiarimenti.
L'utente chiarisce PARZIALMENTE (manca ancora qualcosa).
L'assistant chiede ULTERIORI chiarimenti.
Può risolversi o restare incompleta.""",
        
        """Processo di chiarimento a più step: prima domanda → risposta parziale → altra domanda.
L'assistant è paziente e continua a chiedere finché non ha tutto.""",
        
        """Chiarimento graduale: l'utente fornisce info poco alla volta.
L'assistant raccoglie i pezzi con domande successive."""
    ]
}


# =============================================================================
# USER STYLE BLOCKS - more realistic and varied
# =============================================================================

USER_STYLE_BLOCKS = {
    "formal": [
        """STILE UTENTE: Formale/Professionale.
L'utente usa il "Lei", linguaggio professionale, frasi complete e cortesi.
Esempi reali:
- "Buongiorno, avrei bisogno di assistenza per un problema con il mio conto corrente."
- "Gentilmente, potrebbe verificare lo stato del mio ordine?"
- "Le scrivo in merito alla fattura n. 12345, risulta un importo non corretto."
- "Vorrei richiedere informazioni riguardo all'offerta fibra."

Caratteristiche: forme di cortesia, frasi complete, punteggiatura corretta, niente abbreviazioni.""",
        
        """L'utente parla in modo FORMALE - stile email aziendale.
Come se stesse scrivendo al servizio clienti di un'azienda seria.
Usa "vorrei", "avrei bisogno", "Le chiedo cortesemente".
Frasi grammaticalmente corrette, tono pacato e rispettoso.""",
        
        """Registro FORMALE tipico di clienti business o professionisti.
Esempi:
- "Sarebbe possibile avere un resoconto delle ultime transazioni?"
- "Desidererei procedere con la disdetta del servizio in oggetto."
- "La contatto per segnalare un disservizio riscontrato in data odierna."
"""
    ],
    
    "informal": [
        """STILE UTENTE: Informale/Amichevole.
L'utente usa il "tu", linguaggio colloquiale, tono rilassato.
Esempi reali:
- "Ciao! Mi aiuti a capire come mai non funziona internet?"
- "ehi scusa, dov'è che trovo le info sulla spedizione?"
- "Grazie mille! Ah senti, un'altra cosa..."
- "ok perfetto! allora facciamo così"

Caratteristiche: tu, esclamazioni, emoticon possibili, linguaggio quotidiano.""",
        
        """L'utente è INFORMALE - come se chattasse con un amico.
Usa il tu, può saltare la maiuscola a inizio frase, tono leggero.
Può usare "ok", "bene", "ah", interiezioni colloquiali.
NON è maleducato, solo rilassato.""",
        
        """Registro INFORMALE tipico di giovani utenti o chat casual.
Esempi:
- "hey posso sapere dov'è il mio pacco?"
- "ah ok capito! e quanto ci mette ad arrivare?"
- "senti ma poi come funziona per il reso?"
- "top grazie! ci sentiamo"
"""
    ],
    
    "vague": [
        """STILE UTENTE: Vago/Impreciso.
L'utente NON è specifico, usa riferimenti generici, assume che l'assistant capisca.
Esempi reali:
- "Mi serve quella cosa... il documento che avevamo visto"
- "fammi vedere quello di prima"
- "il problema è con la connessione, credo, o forse il router"
- "non funziona più... non so, da ieri tipo"

L'assistant potrebbe dover chiedere chiarimenti!""",
        
        """L'utente è VAGO - non sa bene cosa vuole o non sa spiegarlo.
Usa "quello", "quella cosa", "il coso", "il servizio".
Può essere confuso o insicuro.
Esempi:
- "c'è un problema con... quella fattura, quella di non so quando"
- "voglio cambiare la cosa... l'offerta insomma"
""",
        
        """Comunicazione VAGA tipica di utenti non tecnici o frettolosi.
Non danno dettagli sufficienti.
Esempi:
- "mi serve aiuto con l'app"  (quale app? che problema?)
- "non funziona" (cosa non funziona?)
- "mandami quel file" (quale file?)
"""
    ],
    
    "telegraphic": [
        """STILE UTENTE: Telegrafico/Ultra-breve.
L'utente scrive il minimo indispensabile, stile SMS/WhatsApp veloce.
Esempi reali:
- "stato ordine 12345"
- "saldo conto"  
- "cambio offerta fibra"
- "prezzo iphone 15"
- "orari apertura"

Niente soggetti, niente verbi, solo keywords essenziali.""",
        
        """L'utente è TELEGRAFICO - scrive come se pagasse a parola.
Stile ricerca Google più che conversazione.
NO frasi complete, NO cortesia, solo l'essenziale.
Esempi:
- "modifica prenotazione 789"
- "spedizione lenta perché"
- "rimborso come"
""",
        
        """Comunicazione TELEGRAFICA - minimalismo estremo.
Utente di fretta o abituato a chatbot rapidi.
Esempi:
- "pw reset"
- "appuntamento martedì mattina"
- "conferma pagamento?"
- "costo roaming usa"
"""
    ],
    
    "frustrated": [
        """STILE UTENTE: Frustrato/Impaziente.
L'utente è arrabbiato o stanco, magari ha già provato altri canali.
Esempi reali:
- "Sono 3 GIORNI che aspetto e nessuno mi risponde!"
- "È la quinta volta che chiamo per questo problema..."
- "Ma è possibile che non riusciate a risolvere una cosa così semplice?"
- "Questo servizio è vergognoso, voglio parlare con un responsabile"

L'assistant deve gestire con calma ed empatia.""",
        
        """L'utente è FRUSTRATO - ha perso la pazienza.
Può usare caps lock, punti esclamativi multipli, tono accusatorio.
NON è offensivo (non generare insulti), ma è chiaramente irritato.
L'assistant deve deescalare e cercare di aiutare.""",
        
        """Cliente ARRABBIATO ma contenuto.
Esempi:
- "Non è accettabile aspettare così tanto per una risposta"
- "Ho già spiegato il problema a tre persone diverse!!!"
- "Perché devo ripetere tutto da capo ogni volta?"
"""
    ],
    
    "confused": [
        """STILE UTENTE: Confuso/Incerto.
L'utente non capisce bene la situazione o come funzionano le cose.
Esempi reali:
- "Scusa non ho capito bene... devo fare cosa esattamente?"
- "Ma quindi... il bonifico è partito o no? Non capisco"
- "E questa opzione che significa? Non sono molto pratico"
- "Mi sono perso, puoi rispiegare dall'inizio?"

L'assistant deve essere paziente e chiaro.""",
        
        """L'utente è CONFUSO - non capisce il processo o la situazione.
Fa domande ripetute, chiede conferme, ammette di non capire.
Può essere anziano, non tecnico, o semplicemente perso.
L'assistant deve semplificare e guidare step by step.""",
        
        """Cliente INCERTO che ha bisogno di rassicurazioni.
Esempi:
- "Quindi se clicco qui... succede cosa?"
- "Scusa sono negato con queste cose, mi spieghi piano?"
- "Non vorrei fare danni, è sicuro procedere?"
"""
    ],
    
    "verbose": [
        """STILE UTENTE: Verboso/Prolisso.
L'utente scrive TROPPO, dà troppi dettagli, divaga.
Esempi reali:
- "Allora, praticamente, ieri stavo cercando di fare un bonifico, perché devo pagare l'affitto, e il mio proprietario mi aveva detto che preferiva il bonifico, e quindi sono andato sull'app, però prima ho dovuto aggiornare l'app perché non funzionava, e poi..."
- "Guarda ti spiego tutto dall'inizio così capisci bene la situazione..."

L'assistant deve estrarre l'essenziale.""",
        
        """L'utente è PROLISSO - racconta tutta la storia della sua vita.
Dà contesto non richiesto, divaga, aggiunge dettagli irrilevanti.
L'assistant deve capire cosa vuole davvero e rispondere in modo focused.""",
        
        """Cliente VERBOSO che scrive wall of text.
Mescola informazioni utili con dettagli superflui.
L'assistant deve identificare il nucleo della richiesta.
"""
    ]
}


# =============================================================================
# SYSTEM PROMPT TYPE BLOCKS - much more varied and realistic
# =============================================================================

SYSTEM_PROMPT_BLOCKS = {
    "none": [
        """SYSTEM PROMPT: Nessuno.
La conversazione NON ha un system prompt. Inizia direttamente con il messaggio dell'utente.
Questo simula chat dove non c'è configurazione iniziale.""",
        
        """Non generare system prompt. La conversazione parte dal primo messaggio user.
Scenario: chatbot generico senza personalizzazione.""",
        
        """System prompt assente. Solo messaggi user/assistant/tool.
L'assistant si comporta come helper generico senza istruzioni specifiche."""
    ],
    
    "minimal": [
        """SYSTEM PROMPT: Minimale (1 frase).
Una sola frase che definisce il ruolo base.
Esempi realistici:
- "Sei un assistente virtuale."
- "You are a helpful AI assistant."
- "Sei qui per aiutare gli utenti."
- "Assistant for customer support."
""",
        
        """System prompt brevissimo, stile produzione.
Esempi:
- "Rispondi in modo utile e conciso."
- "You help users with their requests."
- "Assistente per il supporto clienti."
""",
        
        """System prompt minimo, una riga sola.
Stile enterprise:
- "Customer service assistant - respond helpfully."
- "Assistente digitale per [azienda]."
"""
    ],
    
    "standard": [
        """SYSTEM PROMPT: Standard (2-5 frasi).
Includi:
- Chi è l'assistant
- Cosa fa / in che ambito opera
- Come deve rispondere

Esempio per supporto tecnico:
"Sei l'assistente virtuale per il supporto tecnico. Aiuti i clienti a risolvere problemi con i loro servizi. Rispondi in modo chiaro e professionale. Se non puoi aiutare, indirizza al supporto umano."

Esempio per e-commerce:
"Sei l'assistente di [NomeShop]. Aiuti i clienti con ordini, spedizioni, resi e informazioni sui prodotti. Sii cortese e preciso. Usa i tool disponibili per recuperare informazioni."
""",
        
        """System prompt di media lunghezza con contesto specifico.
Template:
"Sei [ruolo] di [azienda/servizio]. Il tuo compito è [obiettivo principale]. 
Quando rispondi: [stile]. Se necessario, usa i tool per [azioni]."

Adattalo al DOMINIO della conversazione!
""",
        
        """System prompt standard per chatbot aziendale.
Deve contenere:
1. Identità: chi sei
2. Scope: cosa puoi fare
3. Tono: come comunicare
4. Limitazioni: cosa NON fare

Esempio banca:
"Sei l'assistente digitale di [Banca]. Puoi aiutare con saldo, movimenti, bonifici e informazioni sui prodotti. Mantieni un tono professionale ma cordiale. Non fornire mai consigli di investimento personalizzati."
"""
    ],
    
    "detailed": [
        """SYSTEM PROMPT: Dettagliato (6-12 frasi).
System prompt completo stile produzione enterprise.

STRUTTURA:
1. Identità e ruolo (1-2 frasi)
2. Capabilities - cosa può fare (2-3 frasi)  
3. Comportamento e tono (2-3 frasi)
4. Limitazioni e guardrails (2-3 frasi)
5. Istruzioni speciali se necessario

Esempio completo per ISP:
"Sei l'assistente virtuale del servizio clienti di [TelecomProvider]. Il tuo ruolo è supportare i clienti con problemi tecnici, informazioni su contratti, fatturazione e attivazione servizi.

Puoi: verificare lo stato della linea, aprire segnalazioni tecniche, fornire informazioni su offerte e costi, guidare nella configurazione di modem/router.

Rispondi sempre in modo professionale e paziente. Usa un linguaggio chiaro, evitando tecnicismi quando possibile. Se il cliente è frustrato, mostra empatia.

Non puoi: modificare contratti senza autorizzazione, fornire dati sensibili di altri clienti, fare promesse su tempistiche di risoluzione. Se non puoi risolvere, offri di passare a un operatore umano."
""",
        
        """System prompt enterprise dettagliato.
Deve sembrare scritto da un team di prodotto.

Includi sezioni per:
- ROLE: definizione precisa del ruolo
- CAPABILITIES: elenco di cosa può fare
- TONE: guida sullo stile comunicativo  
- BOUNDARIES: cosa non fare
- ESCALATION: quando passare a umano

Adatta tutto al DOMINIO specifico della conversazione!
""",
        
        """System prompt completo con istruzioni operative.
Stile documentation aziendale.

Esempio per supporto software:
"## Ruolo
Sei l'assistente tecnico per [SoftwareName]. Supporti gli utenti nella risoluzione di problemi, configurazione e utilizzo del software.

## Cosa puoi fare
- Diagnosticare problemi comuni
- Guidare nelle configurazioni
- Cercare nella knowledge base
- Aprire ticket di supporto

## Come rispondere
- Sii chiaro e step-by-step
- Chiedi dettagli se la richiesta è vaga
- Conferma sempre prima di eseguire azioni

## Limitazioni
- Non modificare dati utente senza conferma
- Non accedere a sistemi esterni non autorizzati
- Escala a supporto L2 per problemi complessi"
"""
    ]
}


# =============================================================================
# CONVERSATION LENGTH BLOCKS - more detailed
# =============================================================================

CONVERSATION_LENGTH_BLOCKS = {
    "short": [
        """LUNGHEZZA: Breve (2-4 messaggi totali).
Conversazione rapida e concisa. L'utente chiede, l'assistant risponde/agisce, fine.
Tipico di: domande semplici, lookup veloci, conferme.
Esempio flow: User chiede → Assistant risponde (con o senza tool) → eventuale ringraziamento.""",
        
        """Conversazione CORTA: 2-4 messaggi.
Interazione veloce, zero divagazioni.
Scenario: cliente sa già cosa vuole, domanda diretta, risposta diretta.""",
        
        """Genera conversazione BREVE: massimo 4 messaggi.
Tipico del "mordi e fuggi" - utente viene, ottiene info, va via."""
    ],
    
    "medium": [
        """LUNGHEZZA: Media (6-10 messaggi totali).
Conversazione di lunghezza normale. C'è spazio per:
- Chiarimenti iniziali
- La richiesta principale
- Follow-up o domande correlate
- Chiusura naturale

Tipico di: assistenza standard, problemi semplici, richieste con qualche dettaglio.""",
        
        """Conversazione MEDIA: 6-10 messaggi.
Abbastanza spazio per sviluppare l'interazione.
Può includere: saluti, domanda principale, 1-2 follow-up, chiusura.""",
        
        """Lunghezza MEDIA: tra 6 e 10 messaggi.
Conversazione tipica di supporto: contesto → problema → soluzione → conferma."""
    ],
    
    "long": [
        """LUNGHEZZA: Lunga (12-18 messaggi totali).
Conversazione estesa con più scambi:
- Esplorazione del problema
- Tentativi multipli di soluzione
- Approfondimenti
- Possibili cambi di topic correlati

Tipico di: problemi complessi, utenti che fanno molte domande, assistenza approfondita.""",
        
        """Conversazione LUNGA: 12-18 messaggi.
Interazione articolata. L'utente ha bisogno di più supporto.
Può includere: troubleshooting multi-step, domande multiple, riformulazioni.""",
        
        """Lunghezza LUNGA: 12-18 messaggi.
Conversazione complessa con spazio per dettagli, chiarimenti, follow-up multipli."""
    ],
    
    "very_long": [
        """LUNGHEZZA: Molto lunga (20+ messaggi totali).
Conversazione estesa che simula sessioni di assistenza complete:
- Identificazione problema
- Diagnosi
- Tentativi di soluzione
- Escalation o approfondimenti
- Eventuale risoluzione
- Feedback

Tipico di: problemi tecnici complessi, configurazioni, utenti con domande multiple.""",
        
        """Conversazione MOLTO LUNGA: 20+ messaggi.
Sessione di assistenza completa e articolata.
Include: multiple fasi, possibili errori/retry, approfondimenti successivi.""",
        
        """Lunghezza VERY LONG: 20 o più messaggi.
Conversazione tipo "ticket di supporto completo" con tutti i passaggi."""
    ]
}


# =============================================================================
# HISTORY TYPE BLOCKS - more realistic
# =============================================================================

HISTORY_TYPE_BLOCKS = {
    "none": [
        """STORIA PRECEDENTE: Nessuna.
La conversazione inizia DIRETTAMENTE con la richiesta principale.
Niente preamboli, saluti, o contesto precedente.
L'utente va dritto al punto: primo messaggio = già la domanda/richiesta.

Esempio:
User: "Qual è il saldo del mio conto?"
(niente "ciao", "buongiorno", niente contesto)""",
        
        """INIZIO DIRETTO - zero history.
L'utente parte subito con quello che gli serve.
Tipico di: utenti frettolosi, interfacce chatbot, domande semplici.""",
        
        """NO storia precedente, NO saluti.
Primo messaggio = richiesta. Basta."""
    ],
    
    "chitchat": [
        """STORIA PRECEDENTE: Chit-chat iniziale.
La conversazione inizia con saluti e convenevoli PRIMA di arrivare al punto.
Durata chit-chat: 2-4 messaggi di scambio leggero.

Esempio flow:
User: "Ciao!"
Assistant: "Ciao! Come posso aiutarti oggi?"
User: "Tutto bene grazie, senti avrei una domanda..."
→ poi arriva la richiesta vera.""",
        
        """Prima della richiesta c'è SMALL TALK: saluti, come stai, piacere.
Tipico di: utenti italiani, interazioni più umane, canali non-urgent.""",
        
        """CHIT-CHAT iniziale: convenevoli → transizione → richiesta.
L'utente è cordiale, vuole "rompere il ghiaccio" prima di chiedere."""
    ],
    
    "context_setting": [
        """STORIA PRECEDENTE: Context setting.
L'utente SPIEGA LA SITUAZIONE prima di fare la richiesta specifica.
Dà background, motiva il perché, racconta cosa è successo.

Esempio:
User: "Allora, praticamente ho questo problema... la settimana scorsa ho fatto un ordine, è arrivato danneggiato, ho già chiamato il corriere ma mi hanno detto che devo sentire voi..."
→ poi arriva la richiesta specifica (rimborso, reso, etc.)""",
        
        """L'utente fornisce CONTESTO prima della richiesta.
Spiega il background, racconta la storia, motiva la necessità.
SOLO DOPO arriva la richiesta vera e propria.""",
        
        """CONTEXT SETTING: l'utente prepara il terreno.
Racconta cosa è successo, perché è qui, qual è la situazione generale.
L'assistant deve capire il contesto E la richiesta."""
    ],
    
    "previous_tool": [
        """STORIA PRECEDENTE: Tool call già avvenuta.
Nella conversazione c'è GIÀ STATO un tool call PRIMA del punto attuale.
La nuova interazione è un FOLLOW-UP o una richiesta correlata.

Esempio:
(history): User chiede saldo → Assistant chiama get_balance → mostra saldo
(ora): User: "Ok grazie. E le ultime operazioni?" → possibile nuovo tool call

Il contesto del tool precedente può influenzare la nuova richiesta.""",
        
        """C'è già stato almeno UN TOOL CALL nella conversazione.
L'interazione attuale continua da lì: follow-up, approfondimento, domanda correlata.
Il tool precedente ha stabilito un contesto (es. quale conto, quale ordine).""",
        
        """HISTORY CON TOOL: la conversazione ha già visto tool calls.
Ora l'utente fa una richiesta successiva, possibilmente correlata.
L'assistant può fare riferimento ai risultati precedenti."""
    ],
    
    "multi_topic": [
        """STORIA PRECEDENTE: Argomenti multipli.
La conversazione ha già trattato UN ALTRO ARGOMENTO prima.
Ora l'utente passa a una nuova richiesta diversa.

Esempio:
(history): Utente ha chiesto info su fattura → risolto
(ora): User: "Perfetto, grazie. Ah senti, un'altra cosa... come faccio a cambiare la password?"

Argomento NUOVO, non correlato al precedente.""",
        
        """Multi-topic history: la conversazione ha già coperto 1+ argomenti.
Ora si passa a qualcosa di diverso.
L'assistant deve gestire il cambio topic naturalmente.""",
        
        """CAMBIO ARGOMENTO nella storia.
Prima si parlava di X, ora l'utente chiede Y.
Contesti separati, ma stessa sessione."""
    ]
}


# =============================================================================
# PARAM COMPLEXITY BLOCKS - more realistic
# =============================================================================

PARAM_COMPLEXITY_BLOCKS = {
    "explicit": [
        """PARAMETRI: Espliciti (tutti forniti).
L'utente fornisce TUTTI i parametri necessari in modo chiaro e diretto.
L'assistant può chiamare il tool immediatamente senza chiedere nulla.

Esempi realistici:
- "Fammi vedere la pagina 5 del documento 'bilancio_2024.pdf'" 
  → documento: bilancio_2024.pdf, pagina: 5
- "Spedisci il mio ordine 78945 a via Roma 15, Milano, CAP 20121"
  → order_id: 78945, indirizzo completo
- "Prenota un appuntamento per mercoledì 15 gennaio alle 10:00"
  → data: 2024-01-15, ora: 10:00

TUTTO è specificato, niente da inferire.""",
        
        """L'utente è ESPLICITO: dice chiaramente tutti i parametri.
L'assistant NON deve chiedere nulla, può procedere direttamente.
Tutti i campi required del tool sono coperti dalla richiesta.""",
        
        """PARAMETRI COMPLETI nella richiesta.
L'utente ha dato tutte le info necessarie per il tool call.
No ambiguità, no inferenze necessarie."""
    ],
    
    "implicit": [
        """PARAMETRI: Impliciti (da inferire dal contesto).
L'utente NON dice tutto esplicitamente. Alcuni parametri vanno INFERITI dalla conversazione precedente.

Esempi realistici:
- (Contesto: si stava parlando del documento "report_Q3.pdf")
  User: "Mostrami la pagina 2"
  → documento: report_Q3.pdf (implicito dal contesto), pagina: 2 (esplicito)

- (Contesto: l'utente aveva chiesto info sull'ordine 12345)
  User: "Ok, annullalo"
  → order_id: 12345 (implicito dal contesto precedente)

L'assistant DEVE inferire i parametri dal contesto, NON chiedere di nuovo.""",
        
        """L'utente ASSUME che l'assistant ricordi il contesto.
Non ripete informazioni già date: l'assistant deve capirle dal flusso.
Esempi: "quello", "il documento di prima", "l'ordine", senza specificare.""",
        
        """PARAMETRI IMPLICITI: alcuni vanno estratti dalla storia della conversazione.
L'utente non ripete tutto, si riferisce a cose già menzionate."""
    ],
    
    "mixed": [
        """PARAMETRI: Mix espliciti/impliciti.
Alcuni parametri sono detti chiaramente, altri vanno inferiti dal contesto.

Esempi realistici:
- (Contesto: si parlava di "fattura_marzo.pdf")
  User: "Fammi un riassunto di massimo 100 parole"
  → documento: fattura_marzo.pdf (implicito), max_words: 100 (esplicito)

- (Contesto: utente ha un ordine in corso 55555)
  User: "Cambia l'indirizzo di spedizione a via Verdi 8, Napoli"
  → order_id: 55555 (implicito), nuovo indirizzo: completo (esplicito)

L'assistant deve combinare info esplicite + contesto.""",
        
        """MIX di parametri espliciti e impliciti.
Alcuni chiari nella richiesta, altri da dedurre.
L'assistant deve essere intelligente nel ricostruire tutti i parametri.""",
        
        """COMBINAZIONE: l'utente dice alcune cose, altre le lascia al contesto.
Il tool call richiede di mettere insieme esplicito + implicito."""
    ],
    
    "missing": [
        """PARAMETRI: Mancanti (richiesta incompleta).
L'utente NON fornisce alcuni parametri OBBLIGATORI e non sono inferibili dal contesto.
L'assistant DEVE chiedere i parametri mancanti prima di procedere.

Esempi realistici:
- "Prenota un appuntamento" (manca: quando? con chi?)
- "Inviami il documento" (quale documento?)
- "Fai un bonifico" (a chi? quanto? causale?)

L'assistant NON può procedere senza chiedere!""",
        
        """PARAMETRI MANCANTI: la richiesta è incompleta.
Mancano informazioni necessarie che NON si possono inferire.
L'assistant deve chiedere le info mancanti, non inventarle.""",
        
        """RICHIESTA INCOMPLETA: servono parametri che l'utente non ha dato.
L'assistant chiede educatamente le info mancanti prima di agire."""
    ]
}


# =============================================================================
# EDGE CASE BLOCKS - more varied
# =============================================================================

EDGE_CASE_BLOCKS = {
    "topic_change": [
        """CASO SPECIALE: Cambio di argomento.
A un certo punto della conversazione, l'utente CAMBIA completamente ARGOMENTO.

Esempio:
(stavano parlando di fatture)
User: "Ok, capito. Ah senti, completamente altra cosa: come faccio a cambiare password?"

L'assistant deve:
1. Chiudere/acknowledgiare il topic precedente
2. Passare al nuovo argomento naturalmente
3. Eventualmente usare tool diversi per il nuovo topic""",
        
        """TOPIC CHANGE: switch da argomento A ad argomento B.
L'utente finisce con una cosa e ne inizia un'altra.
Transizione può essere brusca o graduale.""",
        
        """L'utente CAMBIA ARGOMENTO durante la conversazione.
Da supporto tecnico a domanda commerciale, o simile.
L'assistant gestisce la transizione fluidamente."""
    ],
    
    "user_correction": [
        """CASO SPECIALE: Correzione dell'utente.
L'utente CORREGGE una sua richiesta precedente dopo che l'assistant ha risposto/agito.

Esempi:
- "No aspetta, intendevo l'altro documento, quello del 2023"
- "Scusa, mi sono sbagliato, volevo pagina 3, non 5"
- "No no, non quel Mario Rossi, l'altro che lavora in contabilità"

L'assistant deve:
1. Acknowledgiare l'errore senza giudicare
2. Correggere e procedere con l'info giusta
3. Eventualmente annullare/rifare l'azione precedente""",
        
        """CORREZIONE: l'utente ha detto una cosa sbagliata e rettifica.
L'assistant si adatta senza frustrazione, corregge il tiro.""",
        
        """L'utente CAMBIA IDEA o si corregge dopo aver visto il risultato.
Esempio: "No scusa, quello non va bene, intendevo..."
L'assistant gestisce il cambio gracefully."""
    ],
    
    "tool_error": [
        """CASO SPECIALE: Errore del tool.
Il tool viene chiamato ma restituisce un ERRORE o risultato vuoto/fallito.

Esempi di errori:
- "Documento non trovato"
- "Errore di connessione al sistema"
- "Utente non autorizzato"
- "Nessun risultato per la ricerca"
- Timeout o exception

L'assistant deve:
1. Comunicare il problema all'utente in modo comprensibile
2. NON mostrare errori tecnici raw
3. Proporre alternative se possibile
4. Eventualmente escalare o riprovare""",
        
        """TOOL FAILURE: la chiamata non va a buon fine.
Errore, risultato vuoto, eccezione, timeout.
L'assistant spiega il problema e cerca soluzioni alternative.""",
        
        """ERRORE nella risposta del tool.
L'assistant gestisce l'errore user-friendly: spiega cosa è successo, cosa si può fare."""
    ],
    
    "ambiguous_request": [
        """CASO SPECIALE: Richiesta ambigua.
La richiesta dell'utente potrebbe essere interpretata in modi diversi.

Esempi:
- "Mandami il report" (quale report? in che formato?)
- "Modifica la prenotazione" (quale prenotazione? come modificarla?)
- "Cerca Mario" (quale Mario? dove cercarlo?)

L'assistant deve chiedere chiarimenti invece di assumere.""",
        
        """AMBIGUITÀ: la richiesta potrebbe voler dire più cose.
L'assistant chiede conferma invece di scegliere arbitrariamente.""",
        
        """Richiesta INTERPRETABILE in modi diversi.
L'assistant chiede quale interpretazione è corretta."""
    ],
    
    "multi_step_task": [
        """CASO SPECIALE: Task multi-step.
La richiesta dell'utente richiede MULTIPLE azioni in sequenza.

Esempio:
User: "Fammi un report delle vendite del mese scorso, mandalo al capo, e poi archivialo"
→ 3 azioni: genera report + invia + archivia

L'assistant può:
- Farle tutte in sequenza (multiple tool calls)
- Confermare prima di procedere
- Spiegare i passaggi mentre li fa""",
        
        """TASK COMPLESSO che richiede più tool calls in sequenza.
L'assistant deve orchestrare multiple azioni.""",
        
        """Richiesta che implica MULTIPLE AZIONI.
L'assistant le esegue in ordine logico, eventualmente confermando."""
    ],
    
    "partial_success": [
        """CASO SPECIALE: Successo parziale.
L'azione riesce PARZIALMENTE: alcuni risultati ok, altri no.

Esempio:
- Ricerca trova 2 documenti su 3 richiesti
- Invio email riuscito a 3 destinatari su 5
- Prenotazione confermata ma con orario diverso

L'assistant deve comunicare sia cosa è andato bene che cosa no.""",
        
        """RISULTATO PARZIALE: qualcosa è riuscito, qualcosa no.
L'assistant comunica entrambi gli esiti chiaramente.""",
        
        """SUCCESSO PARZIALE del tool.
L'assistant spiega cosa è stato completato e cosa no, e propone come procedere."""
    ],
    
    "tool_error_recovery": [
        """═══════════════════════════════════════════════════════════════════════════════
                    CASO CRITICO: RECOVERY DOPO ERRORE TOOL
═══════════════════════════════════════════════════════════════════════════════

SCENARIO FONDAMENTALE PER IL TRAINING:
Questo scenario insegna al modello a NON "arrendersi" dopo un errore.

FLOW OBBLIGATORIO:
1. L'utente chiede qualcosa (es: "mostrami pagina 100 del documento X")
2. L'assistant chiama il tool
3. Il tool restituisce un ERRORE (es: "Errore: pagina 100 non esiste. Il documento ha 45 pagine.")
4. L'assistant spiega l'errore all'utente in modo user-friendly
5. L'utente fa una NUOVA richiesta VALIDA (es: "ok allora dammi pagina 20")
6. ⚠️ L'assistant DEVE CHIAMARE IL TOOL per la nuova richiesta ⚠️

REGOLA CRITICA:
Un errore precedente NON DEVE MAI impedire nuove chiamate tool!
L'assistant NON deve dire "non ho accesso" o "non posso" se il tool esiste.
Per ogni NUOVA richiesta valida, l'assistant DEVE provare a chiamare il tool.

TIPI DI ERRORE DA SIMULARE:
- "Pagina X non esiste, il documento ha Y pagine" → utente chiede pagina valida
- "Documento non trovato" → utente corregge il nome
- "Parametro non valido" → utente riformula correttamente
- "Nessun risultato per la ricerca" → utente cerca altro termine

ESEMPIO CORRETTO:
User: "Mostrami pagina 500 del contratto.pdf"
Assistant: [chiama get_page_content con pagina 500]
Tool: {"error": "Pagina 500 non esiste. Il documento contratto.pdf ha 30 pagine."}
Assistant: "Mi dispiace, il documento ha solo 30 pagine. Quale pagina vorresti vedere?"
User: "Ah ok, allora dammi pagina 15"
Assistant: [DEVE chiamare get_page_content con pagina 15] ← OBBLIGATORIO!
Tool: {"content": "...contenuto pagina 15..."}
Assistant: "Ecco il contenuto della pagina 15..."

═══════════════════════════════════════════════════════════════════════════════""",

        """EDGE CASE: Tool Error → Recovery → Tool Success

QUESTO È UN PATTERN CRITICO che il modello deve imparare:

FASE 1 - ERRORE:
- Utente fa richiesta
- Tool viene chiamato
- Tool restituisce errore (pagina inesistente, documento non trovato, etc.)
- Assistant spiega l'errore gentilmente

FASE 2 - RECOVERY:  
- Utente corregge/modifica la richiesta
- ⚡ L'assistant DEVE chiamare il tool di nuovo ⚡
- Tool questa volta ha successo
- Assistant mostra il risultato

ANTI-PATTERN DA EVITARE:
❌ "Non ho accesso ai documenti" (se i tool esistono!)
❌ "Non posso aiutarti con questo" (se la richiesta è valida!)
❌ Rispondere senza chiamare il tool dopo che l'utente ha corretto

PATTERN CORRETTO:
✅ Chiamare sempre il tool per richieste valide sui documenti
✅ Anche se il tool ha fallito prima, riprovare con nuovi parametri
✅ L'errore precedente è "storia", ogni nuova richiesta merita un tentativo""",

        """SCENARIO: Resilienza agli errori tool

L'utente prova qualcosa, fallisce, corregge, e DEVE funzionare.

Esempi di flow:

1) PAGINA NON ESISTENTE:
   User: "Pagina 999 del manuale"
   → Tool error: "solo 50 pagine"
   User: "Allora pagina 25"
   → Assistant CHIAMA il tool → successo

2) DOCUMENTO SBAGLIATO:
   User: "Riassumi report_2024.pdf"
   → Tool error: "documento non trovato"
   User: "Scusa intendevo report_2023.pdf"
   → Assistant CHIAMA il tool → successo

3) RICERCA SENZA RISULTATI:
   User: "Cerca 'quantum computing' nel contratto"
   → Tool: "nessun risultato"
   User: "Ok cerca 'termini e condizioni'"
   → Assistant CHIAMA il tool → successo

La conversazione DEVE avere almeno 2 tool calls: uno che fallisce, uno che riesce."""
    ]
}


# =============================================================================
# OUTPUT FORMAT INSTRUCTION BLOCK
# =============================================================================

OUTPUT_FORMAT_BLOCKS = [
    """═══════════════════════════════════════════════════════════════════════════════
                              FORMATO OUTPUT OBBLIGATORIO
═══════════════════════════════════════════════════════════════════════════════

Genera una lista di messaggi. Ogni messaggio ha SEMPRE questi campi:
- "role": "user" | "assistant" | "tool"
- "content": stringa o null
- "tool_calls": lista o null
- "tool_call_id": stringa o null

┌─────────────────────────────────────────────────────────────────────────────┐
│ REGOLA FONDAMENTALE: tool_calls va SOLO nei messaggi ASSISTANT              │
│ I messaggi USER non hanno MAI tool_calls!                                   │
└─────────────────────────────────────────────────────────────────────────────┘

SEQUENZA CORRETTA PER UNA TOOL CALL:

1️⃣ USER fa richiesta:
   {"role": "user", "content": "Che tempo fa a Roma?", "tool_calls": null, "tool_call_id": null}

2️⃣ ASSISTANT chiama il tool (content DEVE essere null!):
   {"role": "assistant", "content": null, "tool_calls": [{"id": "tool_call_1", "type": "function", "function": {"name": "get_weather", "arguments": "{\\"city\\": \\"Roma\\"}"}}], "tool_call_id": null}

3️⃣ TOOL risponde:
   {"role": "tool", "content": "{\\"temperature\\": 22, \\"condition\\": \\"soleggiato\\"}", "tool_calls": null, "tool_call_id": "tool_call_1"}

4️⃣ ASSISTANT risponde all'utente:
   {"role": "assistant", "content": "A Roma ci sono 22 gradi e il cielo è soleggiato.", "tool_calls": null, "tool_call_id": null}

⚠️ ERRORI DA EVITARE:
- NON mettere tool_calls nel messaggio USER
- NON mettere content nel messaggio ASSISTANT che chiama un tool
- NON saltare il messaggio ASSISTANT con tool_calls
- arguments DEVE essere una STRINGA JSON escapata, non un oggetto

╔═════════════════════════════════════════════════════════════════════════════╗
║  🚫🚫🚫 DIVIETO ASSOLUTO: NIENTE "RIFLESSIONE" PRIMA DEL TOOL 🚫🚫🚫      ║
╚═════════════════════════════════════════════════════════════════════════════╝

❌ SBAGLIATO - NON FARE MAI COSÌ:
   {"role": "user", "content": "Controlla il meteo a Roma"}
   {"role": "assistant", "content": "Certo, controllo subito il meteo per te."}  ← NO!
   {"role": "assistant", "tool_calls": [...]}  ← Due assistant di fila = ERRORE

✅ CORRETTO - FAI SEMPRE COSÌ:
   {"role": "user", "content": "Controlla il meteo a Roma"}
   {"role": "assistant", "tool_calls": [...]}  ← Chiama il tool DIRETTAMENTE

REGOLA: Quando l'utente chiede qualcosa che richiede un tool:
- L'assistant NON commenta, NON dice "ok", NON dice "certo"
- L'assistant chiama DIRETTAMENTE il tool
- Il messaggio assistant con tool_calls ha content: null

ECCEZIONE: Dopo un tool, l'assistant PUÒ commentare e poi chiamare un altro tool:
   {"role": "tool", "content": "...risultato..."}
   {"role": "assistant", "content": "Ecco i dati. Ora procedo con l'export."}
   {"role": "assistant", "tool_calls": [...]}  ← OK perché prima c'era un tool

═══════════════════════════════════════════════════════════════════════════════"""
]


# =============================================================================
# LANGUAGE BLOCK
# =============================================================================

LANGUAGE_BLOCKS = {
    "it": [
        "La conversazione è interamente in ITALIANO.",
        "Genera la conversazione in ITALIANO.",
        "Lingua: ITALIANO per tutti i messaggi."
    ],
    "en": [
        "The conversation is entirely in ENGLISH.",
        "Generate the conversation in ENGLISH.",
        "Language: ENGLISH for all messages."
    ]
}


# =============================================================================
# TOOL LANGUAGE BLOCK
# =============================================================================

TOOL_LANGUAGE_BLOCKS = {
    "it": [
        "I tool hanno nomi e parametri in ITALIANO.",
        "Tool in ITALIANO: nomi funzioni e parametri sono in italiano."
    ],
    "en": [
        "Tools have names and parameters in ENGLISH.",
        "Tools in ENGLISH: function names and parameters are in English."
    ]
}


# =============================================================================
# CRITICAL CALL-TYPE CONSTRAINTS (cases where tools must NOT be used)
# =============================================================================

CALL_TYPE_CONSTRAINTS = {
    # NEGATIVE - the conversation resolves without any tool
    ("negative", "no_need"): """
═══════════════════════════════════════════════════════════════════════════════
                         SCENARIO: CONVERSAZIONE SENZA TOOL
═══════════════════════════════════════════════════════════════════════════════

Questa è una conversazione dove i tool restano inutilizzati.
L'utente e l'assistant dialogano normalmente, come in una chat amichevole.

Esempi di cosa succede:
- L'utente saluta e chiacchiera → l'assistant risponde cordialmente
- L'utente chiede un'opinione → l'assistant condivide il suo parere
- L'utente fa domande generiche → l'assistant risponde con le sue conoscenze

Nel JSON generato, i messaggi assistant avranno solo "content" (testo normale).
Il campo "tool_calls" sarà vuoto o assente.

Genera una conversazione naturale e piacevole tra umano e assistente.

═══════════════════════════════════════════════════════════════════════════════
""",

    ("negative", "out_of_scope"): """
═══════════════════════════════════════════════════════════════════════════════
                         SCENARIO: RICHIESTA FUORI SCOPE
═══════════════════════════════════════════════════════════════════════════════

Questa è una conversazione dove l'utente chiede qualcosa che i tool presenti 
non possono gestire.

Esempi di cosa succede:
- L'utente chiede di prenotare un volo ma i tool sono per gestione documenti
- L'utente vuole tradurre un testo ma i tool sono per operazioni bancarie
- L'utente chiede qualcosa di molto specifico che esula dalle capacità disponibili

L'assistant:
1. Riconosce gentilmente che la richiesta esula dalle sue capacità attuali
2. Spiega cosa può fare invece
3. Offre alternative o suggerisce dove l'utente potrebbe trovare aiuto

Nel JSON, i messaggi assistant avranno solo "content" testuale.
Conversazione cortese dove l'assistant è trasparente sui suoi limiti.

═══════════════════════════════════════════════════════════════════════════════
""",

    ("negative", "already_answered"): """
═══════════════════════════════════════════════════════════════════════════════
                         SCENARIO: RISPOSTA DIRETTA
═══════════════════════════════════════════════════════════════════════════════

Questa è una conversazione dove l'assistant risponde direttamente 
con le sue conoscenze, senza bisogno di consultare tool esterni.

Esempi tipici:
- "Quanti giorni ha febbraio?" → "28, o 29 negli anni bisestili!"
- "Come si dice 'ciao' in spagnolo?" → "Hola!"
- "Qual è la capitale della Francia?" → "Parigi!"

L'assistant risponde in modo immediato, amichevole e utile.
Usa le conoscenze che già possiede.

Nel JSON generato, i messaggi assistant conterranno solo "content" testuale.
Dialogo semplice e diretto.

═══════════════════════════════════════════════════════════════════════════════
""",

    # CLARIFICATION UNRESOLVED - the user never provides enough info
    ("clarification", "unresolved"): """
═══════════════════════════════════════════════════════════════════════════════
                         SCENARIO: CHIARIMENTO INCOMPLETO
═══════════════════════════════════════════════════════════════════════════════

Questa è una conversazione dove:
1. L'utente fa una richiesta iniziale vaga o incompleta
2. L'assistant chiede gentilmente maggiori dettagli
3. L'utente però non riesce a fornire le informazioni necessarie

Cosa può succedere:
- L'utente dice "non ho il codice con me, riprovo dopo"
- L'utente cambia argomento o rinuncia
- L'utente resta vago perché non sa esattamente cosa vuole

L'assistant è paziente e comprensivo. Alla fine la conversazione si conclude 
senza che l'operazione venga completata.

Nel JSON, i messaggi assistant conterranno solo "content" testuale.
È una conversazione realistica dove le cose non sempre vanno come previsto.

═══════════════════════════════════════════════════════════════════════════════
""",

    # POSITIVE - constraints that force tool usage
    ("positive", "direct"): """
*******************************************************************************
***                    VINCOLO: TOOL CALL OBBLIGATORIO                      ***
*******************************************************************************

✅ DEVI CHIAMARE ALMENO UN TOOL ✅

Questa è una conversazione POSITIVE/DIRECT.
L'utente fa una richiesta chiara → l'assistant DEVE usare un tool.

*** SE NON CHIAMI NESSUN TOOL, L'ESEMPIO È SBAGLIATO ***

*******************************************************************************
""",

    ("positive", "after_chitchat"): """
*******************************************************************************
***                    VINCOLO: TOOL CALL OBBLIGATORIO                      ***
*******************************************************************************

✅ DEVI CHIAMARE ALMENO UN TOOL ✅

Questa è una conversazione POSITIVE/AFTER_CHITCHAT.
Dopo la fase di chit-chat, quando l'utente fa la richiesta specifica,
l'assistant DEVE chiamare il tool appropriato.

*** SE NON CHIAMI NESSUN TOOL, L'ESEMPIO È SBAGLIATO ***

*******************************************************************************
""",

    ("positive", "followup"): """
*******************************************************************************
***                    VINCOLO: TOOL CALLS OBBLIGATORI                      ***
*******************************************************************************

✅ DEVI CHIAMARE PIÙ DI UN TOOL ✅

Questa è una conversazione POSITIVE/FOLLOWUP.
C'è un primo tool call, poi un follow-up che richiede un altro tool.

🚫 DIVIETO RIFLESSIONE: Quando l'utente chiede il follow-up:
   - NON dire "Certo, lo faccio..."
   - CHIAMA IL TOOL DIRETTAMENTE

*** SE NON CHIAMI ALMENO 2 TOOL, L'ESEMPIO È SBAGLIATO ***

*******************************************************************************
""",

    ("positive", "multi_tool"): """
*******************************************************************************
***                    VINCOLO: MULTI TOOL CALL OBBLIGATORIO                ***
*******************************************************************************

✅ DEVI CHIAMARE PIÙ TOOL ✅

Questa è una conversazione POSITIVE/MULTI_TOOL.
La richiesta richiede l'orchestrazione di più tool.

🚫 DIVIETO RIFLESSIONE TRA TOOL:
   - Dopo il risultato di un tool, puoi commentare brevemente
   - Ma NON fare domande all'utente prima di chiamare il prossimo tool
   - Se hai tutto quello che serve → CHIAMA IL TOOL DIRETTAMENTE

*** SE NON CHIAMI ALMENO 2 TOOL, L'ESEMPIO È SBAGLIATO ***

*******************************************************************************
""",

    ("positive", "after_clarification"): """
*******************************************************************************
***                    VINCOLO: TOOL CALL DOPO CHIARIMENTO                  ***
*******************************************************************************

✅ DEVI CHIAMARE UN TOOL DOPO IL CHIARIMENTO ✅

Questa è una conversazione POSITIVE/AFTER_CLARIFICATION.
Prima l'assistant chiede chiarimenti, l'utente risponde,
POI l'assistant DEVE chiamare il tool con le info ottenute.

🚫 DIVIETO RIFLESSIONE: Quando l'utente fornisce le info richieste:
   - NON dire "Perfetto, procedo..."
   - NON dire "Ok, ora che ho tutto..."
   - CHIAMA IL TOOL DIRETTAMENTE

*** SE NON CHIAMI NESSUN TOOL DOPO IL CHIARIMENTO, L'ESEMPIO È SBAGLIATO ***

*******************************************************************************
""",

    ("clarification", "resolved"): """
*******************************************************************************
***                    VINCOLO: TOOL CALL DOPO CHIARIMENTO                  ***
*******************************************************************************

✅ DEVI CHIAMARE UN TOOL DOPO CHE L'UTENTE CHIARISCE ✅

Questa è una conversazione CLARIFICATION/RESOLVED.
L'utente inizia vago, l'assistant chiede chiarimenti,
l'utente fornisce info sufficienti → l'assistant DEVE chiamare il tool.

*** SE NON CHIAMI NESSUN TOOL DOPO IL CHIARIMENTO, L'ESEMPIO È SBAGLIATO ***

*******************************************************************************
""",

    ("clarification", "partial"): """

Questa è una conversazione CLARIFICATION/PARTIAL.

🔴 L'utente NON fornisce MAI TUTTE le informazioni necessarie.
🔴 L'assistant DEVE continuare a chiedere chiarimenti.
🔴 L'assistant NON PUÒ chiamare NESSUN tool perché mancano informazioni.

⚠️ ATTENZIONE: Anche se hai un tool che POTREBBE funzionare con info parziali,
   NON DEVI USARLO. L'assistant deve insistere per avere info complete.

❌ tool_calls: [] deve restare VUOTO per TUTTI i messaggi assistant
❌ Nessun assistant message può avere "tool_calls": [{...}]
❌ Se generi anche UN SOLO tool_call → ESEMPIO INVALIDO

L'assistant NON INVENTA parametri. NON ASSUME valori di default. NON INDOVINA.
La conversazione DEVE finire con l'assistant che chiede ancora info o spiega cosa manca.

*******************************************************************************
"""
}


# =============================================================================
# MAIN FUNCTION: BUILD PROMPT
# =============================================================================

def build_prompt(params: dict, tools: List[dict]) -> str:
    """
    Build the complete prompt from the sampled parameters and the tools.

    Args:
        params: dictionary with the sampled parameters (from SampledParams.to_dict())
        tools: list of tool definitions to include

    Returns:
        the complete prompt to send to the model
    """

    blocks = []

    # 0. Determine call_type and subtype FIRST
    call_type = params["call_type"]
    if call_type == "positive":
        subtype = params["positive_type"]
    elif call_type == "negative":
        subtype = params["negative_reason"]
    else:  # clarification
        subtype = params["clarification_outcome"]

    # 0.1 CRITICAL CONSTRAINT - added at the TOP of the prompt if present
    constraint_key = (call_type, subtype)
    if constraint_key in CALL_TYPE_CONSTRAINTS:
        blocks.append(CALL_TYPE_CONSTRAINTS[constraint_key])

    # 1. Conversation language
    blocks.append(random.choice(LANGUAGE_BLOCKS[params["conversation_language"]]))

    # 2. Tool language
    blocks.append(random.choice(TOOL_LANGUAGE_BLOCKS[params["tool_language"]]))

    # 3. Available tools
    blocks.append(f"TOOL DISPONIBILI:\n{json.dumps(tools, indent=2, ensure_ascii=False)}")

    # 4. System prompt type
    blocks.append(random.choice(SYSTEM_PROMPT_BLOCKS[params["system_prompt_type"]]))

    # 5. Call type + subtype (already determined above)
    blocks.append(random.choice(CALL_TYPE_BLOCKS[(call_type, subtype)]))

    # 6. History type (if applicable)
    if params["first_tool_position"] > 1 or call_type == "negative":
        blocks.append(random.choice(HISTORY_TYPE_BLOCKS[params["history_type"]]))

    # 7. Conversation length
    blocks.append(random.choice(CONVERSATION_LENGTH_BLOCKS[params["conversation_length"]]))

    # 8. User style
    blocks.append(random.choice(USER_STYLE_BLOCKS[params["user_style"]]))

    # 9. Param complexity (only if positive or clarification resolved)
    if params.get("param_complexity"):
        blocks.append(random.choice(PARAM_COMPLEXITY_BLOCKS[params["param_complexity"]]))

    # 10. First tool position (if positive/clarification resolved)
    if params["first_tool_position"] > 0:
        pos = params["first_tool_position"]
        blocks.append(f"POSIZIONE TOOL CALL: Il primo tool call deve avvenire al TURNO {pos} della conversazione (turno 1 = primo messaggio user).")
    
    # 11. Number of tool calls
    if params["num_tool_calls"] > 0:
        blocks.append(f"NUMERO TOOL CALL: L'assistant deve chiamare tool esattamente {params['num_tool_calls']} volta/e nella conversazione.")

    # 12. Edge case (if present)
    if params.get("edge_case") and params["edge_case"] in EDGE_CASE_BLOCKS:
        blocks.append(random.choice(EDGE_CASE_BLOCKS[params["edge_case"]]))

    # 13. Out-of-scope requests - requests the tools cannot satisfy
    if params.get("out_of_scope_requests", 0) > 0:
        n = params["out_of_scope_requests"]
        blocks.append(f"""
════════════════════════════════════════════════════════════════════════════════
                    RICHIESTE FUORI SCOPE ({n})
════════════════════════════════════════════════════════════════════════════════

Durante la conversazione, l'utente farà ANCHE {n} richiesta/e che NON possono essere 
soddisfatte con i tool disponibili. Queste richieste devono essere NATURALI nel 
contesto della conversazione.

ESEMPI di richieste fuori scope (adattale al dominio/contesto):
• "Prenotami un volo" (quando hai solo tool per documenti)
• "Controllami il conto bancario" (quando hai tool per email)
• "Mandami un SMS" (quando hai solo email)
• "Prenota un appuntamento dal dentista" (quando hai solo tool di ricerca)
• "Ordina una pizza" (quando hai tool di produttività)

COMPORTAMENTO CORRETTO dell'assistant per queste richieste:
1. Riconosce il limite - NON inventa capacità che non ha
2. Spiega chiaramente cosa NON può fare
3. Offre alternative pratiche se possibile (es: "Posso prepararti un promemoria" invece di "Non posso prenotare")
4. Continua ad aiutare con le richieste che PUÒ soddisfare

IMPORTANTE: Le richieste fuori scope devono essere DISTRIBUITE nella conversazione,
non tutte alla fine. L'utente chiede cose normali, alcune le risolvi con tool,
altre no perché non hai i tool giusti. Questa è una conversazione realistica!
""")
    
    # 14. Domain
    blocks.append(f"DOMINIO/CONTESTO: {params['domain']}")

    # 15. Output format
    blocks.append(random.choice(OUTPUT_FORMAT_BLOCKS))

    # 16. FINAL REMINDER for tool-less cases - soft version
    if constraint_key in [("clarification", "partial"), ("clarification", "unresolved"), ("negative", "no_need"), ("negative", "already_answered"), ("negative", "out_of_scope")]:
        blocks.append("""
📝 NOTA: In questa conversazione i messaggi dell'assistant contengono solo testo.
        """)
    
    # Assemble the final prompt
    prompt = "\n\n".join(blocks)

    return prompt


def build_system_message() -> str:
    """Build the system message for the generator (teacher) model."""
    
    return """Sei un generatore di dataset per training di modelli LLM su function calling.

Il tuo compito è generare conversazioni REALISTICHE tra un utente e un assistente.
L'assistente ha accesso a dei tool e deve decidere quando usarli.

════════════════════════════════════════════════════════════════════════════════
                         REGOLE CRITICHE SUL FORMATO
════════════════════════════════════════════════════════════════════════════════

1. I messaggi USER hanno SOLO "content". MAI "tool_calls".

2. Quando l'assistant chiama un tool, genera UN MESSAGGIO SEPARATO con:
   - "role": "assistant"
   - "content": null  ← OBBLIGATORIO null!
   - "tool_calls": [{...}]

3. Dopo il tool call, genera il messaggio TOOL con la risposta simulata.

4. Poi l'assistant risponde normalmente con "content" (e tool_calls null).

════════════════════════════════════════════════════════════════════════════════
                              ESEMPIO CORRETTO
════════════════════════════════════════════════════════════════════════════════

Questa sequenza è CORRETTA:

[{"role": "user", "content": "Che tempo fa?", "tool_calls": null, "tool_call_id": null},
 {"role": "assistant", "content": null, "tool_calls": [{"id": "tool_call_1", ...}], "tool_call_id": null},
 {"role": "tool", "content": "{...}", "tool_calls": null, "tool_call_id": "tool_call_1"},
 {"role": "assistant", "content": "Ecco il meteo...", "tool_calls": null, "tool_call_id": null}]

Questa sequenza è SBAGLIATA (tool_calls nel messaggio user):

[{"role": "user", "content": "Che tempo fa?", "tool_calls": [{...}], ...}]  ← ERRORE!

════════════════════════════════════════════════════════════════════════════════

REGOLE AGGIUNTIVE:
- Rispetta ESATTAMENTE le istruzioni (lingua, lunghezza, tipo di call, etc.)
- Quando l'assistant chiama un tool, INVENTA una risposta realistica e coerente
- I parametri dei tool call devono corrispondere ESATTAMENTE allo schema del tool
- "arguments" deve essere una STRINGA JSON, non un oggetto
- Se il tipo è "negative", l'assistant NON deve chiamare tool
- Se il tipo è "clarification/unresolved", l'assistant chiede chiarimenti ma NON chiama tool"""


# =============================================================================
# FUNCTION TO GENERATE A COMPLETE EXAMPLE
# =============================================================================

def generate_api_request(params, tools: List[dict]) -> dict:
    """
    Build the complete request for the chat completions API.

    Args:
        params: sampled parameters (SampledParams or dict)
        tools: tools to use

    Returns:
        dict ready to be passed to the chat.completions.create() call
    """

    # Convert SampledParams to dict if necessary
    if hasattr(params, 'to_dict'):
        params = params.to_dict()
    
    system_msg = build_system_message()
    user_prompt = build_prompt(params, tools)
    
    return {
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt}
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "conversation",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "system_prompt": {
                            "type": ["string", "null"],
                            "description": "Conversation system prompt, null if none"
                        },
                        "messages": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "role": {"type": "string", "enum": ["user", "assistant", "tool"]},
                                    "content": {"type": "string"},
                                    "tool_calls": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "string"},
                                                "type": {"type": "string"},
                                                "function": {
                                                    "type": "object",
                                                    "properties": {
                                                        "name": {"type": "string"},
                                                        "arguments": {"type": "string"}
                                                    },
                                                    "required": ["name", "arguments"],
                                                    "additionalProperties": False
                                                }
                                            },
                                            "required": ["id", "type", "function"],
                                            "additionalProperties": False
                                        }
                                    },
                                    "tool_call_id": {"type": "string"}
                                },
                                "required": ["role"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["messages"],
                    "additionalProperties": False
                }
            }
        },
        "temperature": 1.0
    }

