# ECCE LOGOS: A Latin Morphological Engine

**ECCE LOGOS** is a comprehensive is a comprehensive, rules-based engine written in Python for the complete morphological generation of Latin verbs.

Unlike a dictionary lookup, ECCE LOGOS is a Latin *Brain*. Using its knowledge of phonetics and prosody, it constructs the entire paradigm of a given verb, often generating over 500 unique forms, from just four principal parts and a set of linguistic tags. It is designed to master the vast field of irregularities in macron placement, consonant assimilation, and vowel reduction.

The knowledge base of the engine contains 2,799 verbs, meticulously curated from the entire lexicon used by the orator Cicero.

---
### Demo

The home screen:
![[Ecce Logos 1.jpg]]

search for a verb:
![[Ecce Logos 2.jpg]]

extensive tags [which are all used to generate the paradigms]
![[Ecce Logos 3.jpg]]

---
### Architecture & Key Features

**ECCE LOGOS** is a full-stack Python application designed to model and execute the complex rules of Latin morphology. It is architected as a two-part system: a powerful back-end engine responsible for data processing and linguistic logic, and a custom front-end GUI for user interaction.

#### 1. The Data Layer: A Hand-Crafted Linguistic Database

The foundation of the engine is a proprietary dataset (`verbs.json`), hand-curated from Cicero's complete lexicon. Architecting this dataset was a core part of the project and involved:

*   **Schema Design:** Defining a structured JSON schema to represent each of the 2,799 verbs, capturing not only their principal parts but also a rich set of metadata.
*   **Custom Tagging System:** Creating a custom set of linguistic tags within the schema (e.g., `vowel_gradation_perfect`, `archaic_sigmatic_potential`) to flag verbs for specific phonological transformations, allowing for a clean separation of data from the engine's core logic.
*   **Data Curation:** A significant data management task of manually researching, cataloging, and ensuring the integrity of thousands of verb entries and their associated properties.

#### 2. The Back-End: A Rule-Based Morphological Engine

The "brain" of **Ecce Logos** is an object-oriented `Verb` class that serves as a computational model of a Latin verb. Upon instantiation, it executes a sophisticated pipeline to generate a full paradigm:

*   **Stem Calculation:** Rule-based methods (`_get_present_stem()`, etc.) deduce the verb's core building blocks from its principal parts, correctly handling numerous irregularities.
*   **Algorithmic Conjugation:** Hundreds of logical rules are applied to generate the standard paradigm, correctly handling all regular conjugations, deponent verbs, defective verbs, and major irregulars like `sum` and `ferō`.
*   **Phonological & Historical Modeling:** The engine's most advanced feature is its ability to perform procedural, rule-based transformations. It can reverse-engineer historical sound changes (like nasal infixes) to find a verb's true etymological root and then apply a sequence of phonological rules (e.g., `d/t + s -> ss`, `g/c + s -> x`) to construct historically plausible archaic forms. This includes:
    *   **Syncopated Perfects** (`amāvistī` -> `amāstī`)
    *   **Archaic Sigmatic Futures** (`amāssō`)
    *   **Theoretical Proto-Italic Optatives**
*   **Procedural Generation:** The engine can create and conjugate entirely new verbs that do not exist in the base dataset, demonstrating a deep level of abstraction. This includes:
    *   **Iteratives** (`agō` -> `actitō`)
    *   **Inchoatives** (`amō` -> `amāscō`)
    *   **Desideratives** (`amō` -> `amātūriō`)

#### 3. The Front-End: A Custom Tkinter GUI

The user interface is a custom-built desktop application designed for scholarly research and data exploration. It provides a clean and functional interface for the powerful back-end engine.

*   **Interactive Verb Browser:** The main window loads the entire verb database, providing a live-search filter to allow users to instantly find any verb.
*   **Detailed Paradigm View:** Selecting a verb displays its complete, multi-hundred-form paradigm in a clear, scrollable text view.
*   **Custom Theming & Fonts:** The application uses custom font loading (`pyglet`) and styling to ensure macrons and special characters render correctly, creating a polished and academically appropriate user experience.

---

The following is an example of how a typical verb is stored:

```
  {
    "lemma": "agō",
    "principal_parts": [
      "agere",
      "ēgī",
      "āctum"
    ],
    "conjugation": 3,
    "properties": {
      "perfect": [
        "vowel_gradation_perfect"
      ],
      "supine": [
        "vowel_gradation_supine"
      ],
      "archaic": [
        "archaic_sigmatic_potential(velar)"
      ]
    }
  },
```

---

### Tech Stack & Libraries

*   **Language:** Python 3
*   **GUI Framework:** Tkinter (using `ttk`, `font`, and `scrolledtext` widgets)
*   **Core Logic:** Built with standard libraries including `json` for data handling, `re` for regular expressions, and `itertools` / `copy` for data manipulation.
*   **Custom Font Loading:** `pyglet` is used to load and register the custom font required for proper display of classical Latin characters.

---

### Project Status & Next Steps

**ECCE LOGOS** is a fully functional beta and a living project. My solo venture into combining diachronic phonology with Python is an ongoing process of refinement.

The vast majority of verb paradigms are generated without error. My current development priorities are focused on improving robustness for a few edge cases:

> - **Bug Fix:** Refining the vowel-handling logic for certain compound verbs.
> - **Feature Enhancement:** Expanding the hard-coded paradigms for a handful of highly irregular verbs.

These issues are well understood, and I have a clear path to implementing the solutions in the next version.
