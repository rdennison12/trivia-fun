const categoryUrl = "/api/categories";
const triviaUrl = "/api/proxy";

const amountEl = document.getElementById("amount");
const categoryEl = document.getElementById("category");
const difficultyEl = document.getElementById("difficulty");
const typeEl = document.getElementById("type");
const apiUrlEl = document.getElementById("apiUrl");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const generateBtn = document.getElementById("generateBtn");
const fetchBtn = document.getElementById("fetchBtn");

function setStatus(msg, isError = false) {
    statusEl.textContent = msg;
    statusEl.className = "status" + (isError ? " error" : "");
}

function decodeHtml(text) {
    const t = document.createElement("textarea");
    t.innerHTML = text;
    return t.value;
}

function buildApiUrl() {
    const params = new URLSearchParams();
    const amount = Math.min(50, Math.max(1, Number(amountEl.value)));

    params.set("amount", amount);
    if (categoryEl.value) params.set("category", categoryEl.value);
    if (difficultyEl.value) params.set("difficulty", difficultyEl.value);
    if (typeEl.value) params.set("type", typeEl.value);

    return `${triviaUrl}?${params.toString()}`;
}

function renderQuestions(questions) {
    resultsEl.innerHTML = "";

    questions.forEach((q, index) => {
        const div = document.createElement("div");
        div.className = "question";

        const meta = document.createElement("div");
        meta.className = "meta";
        meta.textContent = `#${index + 1} • ${q.category} • ${q.difficulty} • ${q.type}`;

        const title = document.createElement("div");
        title.textContent = decodeHtml(q.question);

        const answersDiv = document.createElement("div");
        answersDiv.className = "answers";

        const answers = [...q.incorrect_answers, q.correct_answer]
            .map(decodeHtml)
            .sort(() => Math.random() - 0.5);

        answers.forEach(a => {
            const span = document.createElement("div");
            span.className = "answer";
            if (a === decodeHtml(q.correct_answer)) {
                span.classList.add("correct");
            }
            span.textContent = a;
            answersDiv.appendChild(span);
        });

        div.append(meta, title, answersDiv);
        resultsEl.appendChild(div);
    });
}

async function loadCategories() {
    try {
        const res = await fetch(categoryUrl);
        const data = await res.json();

        data.trivia_categories.forEach(cat => {
            const opt = document.createElement("option");
            opt.value = cat.id;
            opt.textContent = cat.name;
            categoryEl.appendChild(opt);
        });

        setStatus("Categories loaded");
    } catch {
        setStatus("Failed to load categories", true);
    }
}

async function fetchQuestions() {
    const url = buildApiUrl();
    apiUrlEl.value = url;

    fetchBtn.disabled = true;
    setStatus("Fetching questions…");

    try {
        const res = await fetch(url);
        const data = await res.json();

        if (data.response_code !== 0) {
            setStatus("No questions available for these settings", true);
            return;
        }

        renderQuestions(data.results);
        setStatus(`Loaded ${data.results.length} questions`);
    } catch {
        setStatus("Error fetching questions", true);
    } finally {
        setTimeout(() => (fetchBtn.disabled = false), 5000);
    }
}

generateBtn.addEventListener("click", () => {
    apiUrlEl.value = buildApiUrl();
    setStatus("API URL generated");
});

fetchBtn.addEventListener("click", fetchQuestions);

[amountEl, categoryEl, difficultyEl, typeEl].forEach(el => {
    el.addEventListener("change", () => {
        apiUrlEl.value = buildApiUrl();
    });
});

apiUrlEl.value = buildApiUrl();
loadCategories();
``