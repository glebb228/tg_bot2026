import fs from "node:fs/promises";
import path from "node:path";

const {
  Presentation,
  PresentationFile,
  row,
  column,
  grid,
  layers,
  text,
  rule,
  shape,
  fill,
  hug,
  fixed,
  wrap,
  fr,
  auto,
  drawSlideToCtx,
} = await import("@oai/artifact-tool");

const { Canvas } = await import(
  "/Users/glebkozlov/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/node_modules/skia-canvas/lib/index.mjs"
);

const workspaceDir = "/Users/glebkozlov/Desktop/tg_bot2026/presentation";
const outputDir = path.join(workspaceDir, "output");
const scratchDir = path.join(workspaceDir, "scratch");
const previewDir = path.join(scratchDir, "previews");

await fs.mkdir(outputDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });

const colors = {
  ink: "#17324D",
  softInk: "#4B6178",
  accent: "#1F7AE0",
  accentSoft: "#DDEBFB",
  mint: "#DDF4EE",
  line: "#C8D7E8",
  pale: "#F5F9FD",
  white: "#FFFFFF",
};

const fonts = {
  title: "Georgia",
  body: "Trebuchet MS",
};

const presentation = Presentation.create({
  slideSize: { width: 1920, height: 1080 },
});

function txt(value, fontSize, options = {}) {
  return text(value, {
    width: options.width ?? fill,
    height: options.height ?? hug,
    name: options.name,
    style: {
      fontFace: options.fontFace ?? fonts.body,
      fontSize,
      color: options.color ?? colors.ink,
      bold: options.bold ?? false,
      italic: options.italic ?? false,
      align: options.align ?? "left",
    },
  });
}

function bulletList(items, width = fill) {
  return txt(
    items.map((item) => `• ${item}`).join("\n\n"),
    26,
    {
      color: colors.softInk,
      width,
    },
  );
}

function sectionNumber(value) {
  return txt(value, 180, {
    fontFace: fonts.title,
    color: "#EEF4FB",
    bold: true,
    width: fixed(420),
    align: "right",
    name: `section-number-${value}`,
  });
}

function topBand(title, subtitle) {
  return column(
    { width: fill, height: hug, gap: 20, name: "top-band" },
    [
      txt(title, 54, {
        fontFace: fonts.title,
        bold: true,
        color: colors.ink,
        width: wrap(980),
        name: "slide-title",
      }),
      rule({
        name: "title-rule",
        width: fixed(240),
        stroke: colors.accent,
        weight: 5,
      }),
      txt(subtitle, 24, {
        width: wrap(920),
        color: colors.softInk,
        name: "subtitle",
      }),
    ],
  );
}

function addSlide(content, bg = colors.white) {
  const slide = presentation.slides.add();
  slide.compose(
    layers(
      { width: fill, height: fill, name: "slide-root" },
      [
        shape({
          name: "background",
          width: fill,
          height: fill,
          fill: bg,
        }),
        content,
      ],
    ),
    {
      frame: { left: 0, top: 0, width: 1920, height: 1080 },
      baseUnit: 8,
    },
  );
  return slide;
}

addSlide(
  column(
    {
      width: fill,
      height: fill,
      padding: { x: 88, y: 72 },
      gap: 28,
      name: "cover-grid",
    },
    [
      column(
        { width: fill, height: hug, gap: 18, name: "cover-header" },
        [
          txt("Telegram-бот для изучения иностранных языков", 58, {
            fontFace: fonts.title,
            bold: true,
            width: wrap(1200),
            name: "slide-title",
          }),
          txt("Учебный проект. MVP по спринтам 1–5", 28, {
            color: colors.accent,
            bold: true,
            width: wrap(720),
          }),
        ],
      ),
      txt("2026", 190, {
        fontFace: fonts.title,
        bold: true,
        color: "#E5EEF8",
        width: fill,
        align: "right",
      }),
      txt(
        "Проект демонстрирует рабочий MVP Telegram-бота: обучение словам, тренировки, словарь, прогресс, настройки и напоминания.",
        30,
        { width: wrap(980), color: colors.softInk },
      ),
      bulletList(
        [
          "Язык разработки: Python",
          "Библиотека Telegram API: aiogram",
          "Хранение данных: PostgreSQL / SQLite fallback и SQLAlchemy",
          "Интерфейс: команды и inline-кнопки",
        ],
        wrap(760),
      ),
      txt("tg_bot2026", 18, {
        color: colors.softInk,
        italic: true,
        width: fill,
        name: "source",
      }),
    ],
  ),
  colors.pale,
);

addSlide(
  grid(
    {
      width: fill,
      height: fill,
      columns: [fr(1.1), fr(0.9)],
      rows: [auto, fr(1)],
      columnGap: 56,
      rowGap: 26,
      padding: { x: 88, y: 72 },
    },
    [
      topBand(
        "Цель и задачи проекта",
        "Цель проекта — создать MVP Telegram-бота для изучения английской лексики с учебными карточками, тренировками и сохранением прогресса.",
      ),
      sectionNumber("01"),
      bulletList(
        [
          "Выбрать язык программирования и библиотеку для разработки Telegram-бота.",
          "Спроектировать архитектуру приложения и схему базы данных.",
          "Подготовить детальную схему пользовательских диалогов.",
          "Реализовать базу данных, регистрацию пользователя и хранение прогресса.",
          "Добавить карточки, словарь, тренировки и настройки.",
          "Подготовить проект к демонстрации и дальнейшему деплою.",
        ],
      ),
      column(
        { width: fill, height: hug, gap: 18, name: "goal-note" },
        [
          txt("Результат спринта 1", 24, {
            color: colors.accent,
            bold: true,
          }),
          txt(
            "Концепция проекта, схема БД, карта пользовательских переходов и подготовленный репозиторий.",
            24,
            { color: colors.softInk, width: wrap(500) },
          ),
          txt("Результат MVP", 24, {
            color: colors.accent,
            bold: true,
          }),
          txt(
            "Работающий бот с карточками, словарем, тестами, прогрессом, уровнями и напоминаниями.",
            24,
            { color: colors.softInk, width: wrap(500) },
          ),
        ],
      ),
    ],
  ),
);

addSlide(
  grid(
    {
      width: fill,
      height: fill,
      columns: [fr(1), fr(1)],
      rows: [auto, fr(1)],
      columnGap: 48,
      rowGap: 28,
      padding: { x: 88, y: 72 },
    },
    [
      topBand(
        "Выбранный стек технологий",
        "Технологический стек подобран так, чтобы обеспечить простую реализацию MVP и возможность дальнейшего расширения проекта.",
      ),
      sectionNumber("02"),
      column(
        { width: fill, height: hug, gap: 22, name: "stack-left" },
        [
          txt("Основные технологии", 30, {
            bold: true,
            color: colors.accent,
          }),
          bulletList(
            [
              "Python 3.11+",
              "aiogram 3 для работы с Telegram Bot API",
              "SQLAlchemy 2 как ORM-слой",
              "PostgreSQL как основная БД и SQLite для локального запуска",
            ],
            fill,
          ),
        ],
      ),
      column(
        { width: fill, height: hug, gap: 22, name: "stack-right" },
        [
          txt("Причины выбора", 30, {
            bold: true,
            color: colors.accent,
          }),
          bulletList(
            [
              "Python обеспечивает высокую скорость разработки и хорошую читаемость кода.",
              "aiogram поддерживает команды, callback-кнопки и удобную маршрутизацию.",
              "SQLAlchemy упрощает работу с моделями и последующее масштабирование.",
              "PostgreSQL подходит для большего числа пользователей и серверного деплоя.",
            ],
            fill,
          ),
        ],
      ),
    ],
  ),
);

addSlide(
  grid(
    {
      width: fill,
      height: fill,
      columns: [fr(0.9), fr(1.1)],
      rows: [auto, fr(1)],
      columnGap: 54,
      rowGap: 28,
      padding: { x: 88, y: 72 },
    },
    [
      topBand(
        "Архитектура приложения",
        "Проект организован по модульному принципу: конфигурация, база данных, обработчики, клавиатуры и сервисная логика разделены по отдельным пакетам.",
      ),
      sectionNumber("03"),
      column(
        { width: fill, height: hug, gap: 16, name: "arch-left" },
        [
          txt("Ключевые модули", 28, {
            color: colors.accent,
            bold: true,
          }),
          bulletList(
            [
              "main.py — запуск приложения и polling",
              "config.py — загрузка BOT_TOKEN и DATABASE_URL",
              "database/ — engine, session и модели",
              "handlers/ — /start и обработка callback-кнопок",
              "keyboards/ — главное меню",
              "services/ — регистрация и поиск пользователя",
            ],
            fill,
          ),
        ],
      ),
      column(
        { width: fill, height: hug, gap: 18, name: "arch-right" },
        [
          txt("Логика работы", 28, {
            color: colors.accent,
            bold: true,
          }),
          txt(
            "1. Приложение загружает конфигурацию и инициализирует базу данных.",
            24,
            { color: colors.softInk },
          ),
          txt(
            "2. Пользователь отправляет команду /start, после чего бот получает данные Telegram-профиля.",
            24,
            { color: colors.softInk },
          ),
          txt(
            "3. Через сервисный слой выполняется поиск пользователя в БД и создание новой записи при необходимости.",
            24,
            { color: colors.softInk },
          ),
          txt(
            "4. После регистрации пользователю отправляется приветствие и отображается меню разделов.",
            24,
            { color: colors.softInk },
          ),
        ],
      ),
    ],
  ),
);

addSlide(
  grid(
    {
      width: fill,
      height: fill,
      columns: [fr(1), fr(1)],
      rows: [auto, fr(1)],
      columnGap: 52,
      rowGap: 28,
      padding: { x: 88, y: 72 },
    },
    [
      topBand(
        "Схема базы данных",
        "База данных хранит пользователей, учебные темы, карточки, словарь, прогресс, попытки тестов и настройки напоминаний.",
      ),
      sectionNumber("04"),
      column(
        { width: fill, height: hug, gap: 18, name: "db-left" },
        [
          txt("Основные таблицы", 30, {
            color: colors.accent,
            bold: true,
          }),
          bulletList(
            [
              "users — профиль пользователя, уровень и настройки",
              "word_sets — учебные темы и служебные типы тестов",
              "word_cards — карточки слов с переводами и примерами",
              "user_words — личный словарь пользователя",
              "user_word_progress — прогресс по конкретным словам",
              "quiz_attempts — история прохождения тестов",
            ],
            fill,
          ),
        ],
      ),
      column(
        { width: fill, height: hug, gap: 18, name: "db-right" },
        [
          txt("Назначение модели", 30, {
            color: colors.accent,
            bold: true,
          }),
          bulletList(
            [
              "Сохранение информации о новом пользователе при первом запуске.",
              "Основа для последующей персонализации сценариев обучения.",
              "Хранение учебных тем, карточек, словаря, прогресса и попыток тестов.",
              "Поддержка PostgreSQL для дальнейшего деплоя и SQLite для локальной демонстрации.",
            ],
            fill,
          ),
        ],
      ),
    ],
  ),
);

addSlide(
  grid(
    {
      width: fill,
      height: fill,
      columns: [fr(1.05), fr(0.95)],
      rows: [auto, fr(1)],
      columnGap: 52,
      rowGap: 28,
      padding: { x: 88, y: 72 },
    },
    [
      topBand(
        "Сценарии взаимодействия пользователя",
        "В рамках проектирования была подготовлена полная схема пользовательских диалогов, описывающая основные переходы между экранами и разделами.",
      ),
      sectionNumber("05"),
      column(
        { width: fill, height: hug, gap: 16, name: "flow-left" },
        [
          txt("Базовый маршрут", 28, {
            color: colors.accent,
            bold: true,
          }),
          txt("Открытие бота → /start → проверка пользователя → регистрация → приветствие → главное меню", 28, {
            color: colors.ink,
            width: wrap(760),
          }),
          rule({ width: fill, stroke: colors.line, weight: 2 }),
          txt("Основные разделы", 28, {
            color: colors.accent,
            bold: true,
          }),
          bulletList(
            [
              "Уроки",
              "Тренировка",
              "Тема дня",
              "Мой словарь",
              "Прогресс",
              "Настройки",
            ],
            fill,
          ),
        ],
      ),
      column(
        { width: fill, height: hug, gap: 18, name: "flow-right" },
        [
          txt("Что отражено в полной схеме", 28, {
            color: colors.accent,
            bold: true,
          }),
          bulletList(
            [
              "Просмотр карточек по темам и уровню пользователя.",
              "Обычный тест, повторение ошибок, тест по словарю и режим до первой ошибки.",
              "Добавление, тестирование и удаление слов из личного словаря.",
              "Просмотр статистики, цели дня и слабых слов.",
              "Выбор уровня и настройка напоминаний.",
              "Возврат из каждого раздела в главное меню.",
            ],
            fill,
          ),
        ],
      ),
    ],
  ),
);

addSlide(
  grid(
    {
      width: fill,
      height: fill,
      columns: [fr(1), fr(1)],
      rows: [auto, fr(1)],
      columnGap: 48,
      rowGap: 28,
      padding: { x: 88, y: 72 },
    },
    [
      topBand(
        "Реализованный функционал",
        "В MVP реализованы ключевые сценарии обучения: карточки, словарь, тесты, прогресс, настройки и напоминания.",
      ),
      sectionNumber("06"),
      column(
        { width: fill, height: hug, gap: 18, name: "done-left" },
        [
          txt("Реализовано в коде", 30, {
            color: colors.accent,
            bold: true,
          }),
          bulletList(
            [
              "45 учебных тем и 396 карточек с примерами.",
              "Регистрация пользователя и хранение профиля в БД.",
              "Личный словарь с ручным добавлением и удалением слов.",
              "Тесты по темам, словарю и слабым словам.",
              "Режим до первой ошибки и вызов выше уровня.",
            ],
            fill,
          ),
        ],
      ),
      column(
        { width: fill, height: hug, gap: 18, name: "done-right" },
        [
          txt("Подготовлено к развитию", 30, {
            color: colors.accent,
            bold: true,
          }),
          bulletList(
            [
              "Прогресс: точность, цель дня, слабые слова и сильная тема.",
              "Настройки уровня и напоминаний.",
              "Поддержка PostgreSQL и локального SQLite fallback.",
              "Обработка текстовых сообщений и устаревших кнопок.",
            ],
            fill,
          ),
        ],
      ),
    ],
  ),
);

addSlide(
  grid(
    {
      width: fill,
      height: fill,
      columns: [fr(1.05), fr(0.95)],
      rows: [auto, fr(1), auto],
      columnGap: 48,
      rowGap: 24,
      padding: { x: 88, y: 72 },
    },
    [
      topBand(
        "Итоги работы",
        "В результате практики была создана рабочая основа Telegram-бота, готовая к демонстрации и дальнейшему развитию.",
      ),
      sectionNumber("07"),
      column(
        { width: fill, height: hug, gap: 18, name: "results-left" },
        [
          txt("Основные результаты", 30, {
            color: colors.accent,
            bold: true,
          }),
          bulletList(
            [
              "Разработан рабочий Telegram-бот на Python и aiogram.",
              "Реализованы карточки, тренировки, словарь и прогресс.",
              "Настроена база данных через SQLAlchemy.",
              "Добавлены пользовательские настройки и напоминания.",
              "Подготовлены README, схема БД, архитектура и user flow.",
            ],
            fill,
          ),
        ],
      ),
      column(
        { width: fill, height: hug, gap: 18, name: "results-right" },
        [
          txt("Следующий этап", 30, {
            color: colors.accent,
            bold: true,
          }),
          bulletList(
            [
              "Развертывание бота на сервере для постоянного аптайма.",
              "Подключение production PostgreSQL.",
              "Добавление Alembic для версионирования миграций.",
              "Расширение контента и дальнейшая стабилизация.",
            ],
            fill,
          ),
        ],
      ),
      txt("Репозиторий: github.com/glebb228/tg_bot2026", 20, {
        color: colors.softInk,
        italic: true,
        columnSpan: 2,
        width: fill,
        name: "source",
      }),
    ],
  ),
  "#F8FBFE",
);

const pptxBlob = await PresentationFile.exportPptx(presentation);
await pptxBlob.save(path.join(outputDir, "output.pptx"));

const previewPaths = [];
for (let index = 0; index < presentation.slides.items.length; index += 1) {
  const slide = presentation.slides.items[index];
  const canvas = new Canvas(1920, 1080);
  const ctx = canvas.getContext("2d");
  await drawSlideToCtx(slide, presentation, ctx);
  const previewPath = path.join(previewDir, `slide-${String(index + 1).padStart(2, "0")}.png`);
  await fs.writeFile(previewPath, await canvas.png);
  previewPaths.push(previewPath);
}

await fs.writeFile(
  path.join(scratchDir, "preview-index.json"),
  `${JSON.stringify({ previewPaths }, null, 2)}\n`,
  "utf8",
);

console.log(
  JSON.stringify(
    {
      pptx: path.join(outputDir, "output.pptx"),
      previewPaths,
    },
    null,
    2,
  ),
);
