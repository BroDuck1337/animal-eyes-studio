# 🐜 Animal Eyes Studio

> An AI Story Orchestrator for Consistent Wildlife Video Generation.

Animal Eyes Studio is an AI-powered story orchestration framework designed to solve one of the biggest problems in current AI video generation:

> **Scene inconsistency.**

Instead of generating isolated prompts for each scene, Animal Eyes Studio builds a complete story structure, tracks world state, and generates coherent scene information before any prompt reaches a video generation model.

---

# 🎯 Goal

Most AI video generators work like this:

Topic

↓

Script

↓

Prompt

↓

Video

This often produces:

- Different characters
- Different environments
- Different lighting
- Random transitions
- Broken story flow

Animal Eyes Studio changes the pipeline into:

Topic

↓

Story Bible

↓

Timeline

↓

Scene State

↓

Prompt Builder

↓

Video Generator

Every scene knows:

- Who the character is
- Where the story happens
- What already happened
- Current world state
- Story progression

---

# 🏗 Architecture

Topic

↓

Story Bible

↓

Timeline Engine

↓

State Engine

↓

Scene Generator

↓

Prompt Generator

↓

Video Generator (MoneyPrinter / Veo / Kling / Runway)

---

# 📂 Project Structure

```
animal-eyes-studio/

├── core/
│   ├── story_bible.py
│   ├── timeline_engine.py
│   ├── state_engine.py
│   ├── character_engine.py
│   ├── world_engine.py
│   └── consistency_engine.py
│
├── generators/
│   ├── script_generator.py
│   ├── scene_generator.py
│   ├── prompt_generator.py
│   ├── thumbnail_generator.py
│   └── seo_generator.py
│
├── models/
│   ├── character.py
│   ├── world.py
│   ├── story_event.py
│   ├── timeline_scene.py
│   └── scene_state.py
│
├── templates/
│   ├── wildlife/
│   ├── ocean/
│   └── survival/
│
├── outputs/
│   ├── bible/
│   ├── scenes/
│   ├── prompts/
│   └── package/
│
└── app.py
```

---

# 📖 Story Bible

The Story Bible is the single source of truth for every generated project.

It stores:

- Character
- World
- Timeline
- Story Type
- Duration
- Rules

Every component in the pipeline reads from the Story Bible.

---

# 🧍 Character Engine

Responsible for maintaining consistent characters.

Stores:

- Character ID
- Species
- Appearance
- Role
- Persistent attributes

---

# 🌍 World Engine

Defines the story universe.

Stores:

- Ecosystem
- Season
- Weather
- Lighting
- Environment rules

---

# ⏳ Timeline Engine

Converts a Story Bible into an ordered sequence of scenes.

Each Timeline Scene contains:

- Scene ID
- Start Time
- End Time
- Duration
- Event
- Summary
- Location
- Mood
- Intensity

---

# 🎬 Scene State

Unlike TimelineScene, SceneState stores the dynamic state of the world.

Example:

- Character status
- Food
- Danger
- Weather
- Lighting
- Camera state
- Environment state

TimelineScene answers:

> What happens?

SceneState answers:

> What is the world like when it happens?

---

# 🎥 Prompt Generator

Prompt generation is deterministic.

Each prompt is generated from:

Story Bible

+

Timeline Scene

+

Scene State

Instead of only:

Topic

↓

GPT

↓

Prompt

---

# 🔄 Consistency Engine

Ensures every generated prompt follows the same story.

Maintains:

- Character consistency
- Environment consistency
- Story continuity
- Visual continuity

---

# 📦 Output Package

A completed project exports:

```
project/

story_bible.json

script.txt

scene_01.json

scene_02.json

...

prompt_01.txt

prompt_02.txt

thumbnail_prompt.txt

description.txt

hashtags.txt
```

---

# 🚀 Future Roadmap

## Phase 1

- Story Bible
- Timeline Engine
- State Engine

## Phase 2

- Scene Generator
- Prompt Builder

## Phase 3

- Video Adapters
  - MoneyPrinterTurbo
  - Veo
  - Kling
  - Runway

## Phase 4

- Visual Consistency
- Image Chaining
- Reference Frame Generation

## Phase 5

- Multi-Agent Story Planning
- Automatic Prompt Optimization
- Full AI Video Production Pipeline

---

# 💡 Vision

Animal Eyes Studio is not another video generator.

It is an **AI Story Orchestrator**.

Its mission is to transform a simple topic into a fully structured, coherent, and consistent story that any modern AI video model can understand and render reliably.# 🐜 Animal Eyes Studio

> An AI Story Orchestrator for Consistent Wildlife Video Generation.

Animal Eyes Studio is an AI-powered story orchestration framework designed to solve one of the biggest problems in current AI video generation:

> **Scene inconsistency.**

Instead of generating isolated prompts for each scene, Animal Eyes Studio builds a complete story structure, tracks world state, and generates coherent scene information before any prompt reaches a video generation model.

---

# 🎯 Goal

Most AI video generators work like this:

Topic

↓

Script

↓

Prompt

↓

Video

This often produces:

- Different characters
- Different environments
- Different lighting
- Random transitions
- Broken story flow

Animal Eyes Studio changes the pipeline into:

Topic

↓

Story Bible

↓

Timeline

↓

Scene State

↓

Prompt Builder

↓

Video Generator

Every scene knows:

- Who the character is
- Where the story happens
- What already happened
- Current world state
- Story progression

---

# 🏗 Architecture

Topic

↓

Story Bible

↓

Timeline Engine

↓

State Engine

↓

Scene Generator

↓

Prompt Generator

↓

Video Generator (MoneyPrinter / Veo / Kling / Runway)

---

# 📂 Project Structure

```
animal-eyes-studio/

├── core/
│   ├── story_bible.py
│   ├── timeline_engine.py
│   ├── state_engine.py
│   ├── character_engine.py
│   ├── world_engine.py
│   └── consistency_engine.py
│
├── generators/
│   ├── script_generator.py
│   ├── scene_generator.py
│   ├── prompt_generator.py
│   ├── thumbnail_generator.py
│   └── seo_generator.py
│
├── models/
│   ├── character.py
│   ├── world.py
│   ├── story_event.py
│   ├── timeline_scene.py
│   └── scene_state.py
│
├── templates/
│   ├── wildlife/
│   ├── ocean/
│   └── survival/
│
├── outputs/
│   ├── bible/
│   ├── scenes/
│   ├── prompts/
│   └── package/
│
└── app.py
```

---

# 📖 Story Bible

The Story Bible is the single source of truth for every generated project.

It stores:

- Character
- World
- Timeline
- Story Type
- Duration
- Rules

Every component in the pipeline reads from the Story Bible.

---

# 🧍 Character Engine

Responsible for maintaining consistent characters.

Stores:

- Character ID
- Species
- Appearance
- Role
- Persistent attributes

---

# 🌍 World Engine

Defines the story universe.

Stores:

- Ecosystem
- Season
- Weather
- Lighting
- Environment rules

---

# ⏳ Timeline Engine

Converts a Story Bible into an ordered sequence of scenes.

Each Timeline Scene contains:

- Scene ID
- Start Time
- End Time
- Duration
- Event
- Summary
- Location
- Mood
- Intensity

---

# 🎬 Scene State

Unlike TimelineScene, SceneState stores the dynamic state of the world.

Example:

- Character status
- Food
- Danger
- Weather
- Lighting
- Camera state
- Environment state

TimelineScene answers:

> What happens?

SceneState answers:

> What is the world like when it happens?

---

# 🎥 Prompt Generator

Prompt generation is deterministic.

Each prompt is generated from:

Story Bible

+

Timeline Scene

+

Scene State

Instead of only:

Topic

↓

GPT

↓

Prompt

---

# 🔄 Consistency Engine

Ensures every generated prompt follows the same story.

Maintains:

- Character consistency
- Environment consistency
- Story continuity
- Visual continuity

---

# 📦 Output Package

A completed project exports:

```
project/

story_bible.json

script.txt

scene_01.json

scene_02.json

...

prompt_01.txt

prompt_02.txt

thumbnail_prompt.txt

description.txt

hashtags.txt
```

---

# 🚀 Future Roadmap

## Phase 1

- Story Bible
- Timeline Engine
- State Engine

## Phase 2

- Scene Generator
- Prompt Builder

## Phase 3

- Video Adapters
  - MoneyPrinterTurbo
  - Veo
  - Kling
  - Runway

## Phase 4

- Visual Consistency
- Image Chaining
- Reference Frame Generation

## Phase 5

- Multi-Agent Story Planning
- Automatic Prompt Optimization
- Full AI Video Production Pipeline

---

# 💡 Vision

Animal Eyes Studio is not another video generator.

It is an **AI Story Orchestrator**.

Its mission is to transform a simple topic into a fully structured, coherent, and consistent story that any modern AI video model can understand and render reliably.