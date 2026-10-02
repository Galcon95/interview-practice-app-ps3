# IntervAI User Manual

IntervAI helps you prepare for job interviews in IT and tech. You can:

- **practice interview questions** for your role and level,
- get **smart questions to ask the interviewer**,
- **analyze a job posting** (as text or as screenshots) to see the role, the
  seniority and the skills it asks for.

Two more tools, the **Intro Polisher** and the **Resume Matcher**, are coming
soon.

## Contents

1. [Getting started](#1-getting-started)
2. [The Home page](#2-the-home-page)
3. [Role Q&A: practice questions](#3-role-qa-practice-questions)
4. [JD Analyzer: understand a job posting](#4-jd-analyzer-understand-a-job-posting)
5. [Coming soon](#5-coming-soon)
6. [AI settings (sidebar)](#6-ai-settings-sidebar)
7. [Limits and safety](#7-limits-and-safety)
8. [Messages and what to do](#8-messages-and-what-to-do)
9. [Tips](#9-tips)

---

## 1. Getting started

**Opening the app.** Whoever set up the app starts it with the command below,
from the project folder. It then opens in your browser at
<http://localhost:8501>.

```bash
streamlit run client/app.py
```

**Finding your way around.**

| Area | What it holds |
|---|---|
| **Menu** (top bar) | Home · Role Q&A · JD Analyzer · Intro Polisher · Resume Matcher |
| **Sidebar** (dark panel on the left) | AI settings: model, temperature, max tokens (see [section 6](#6-ai-settings-sidebar)) |
| **Page** (middle) | The tool you picked in the menu |

If the sidebar is hidden, open it with the small arrow at the top left.

**What the app remembers.** Your results and texts stay while you switch
between pages. If you **reload the browser tab** or close it, they're gone.
Copy anything you want to keep.

---

## 2. The Home page

The Home page gives you an overview:

- Two buttons take you straight to work: **Analyze a job description** and
  **Practice Role Q&A**.
- **How it works** shows the steps in short.
- One card per tool. Tools you can use say **Open**; the others say **Coming
  soon**.
- The dark **security** section shows which safety checks are on (see
  [section 7](#7-limits-and-safety)).

---

## 3. Role Q&A: practice questions

Use this page when you know which kind of job you're applying for.

### Step by step

1. Open **Role Q&A** in the menu.
2. Pick your **Role** and **Level**:

   | Roles | Levels |
   |---|---|
   | Frontend Developer, Backend Developer, Full-Stack Developer, DevOps / SRE, Data / AI Engineer, QA Engineer | Junior, Mid, Senior, Lead |

3. Choose what you need. The page has two panels, each with its own button:

   - **Interview questions** → click **Generate interview questions**. You
     get 5 questions an interviewer might ask you.
   - **Questions to ask the interviewer** → click **Generate reverse
     questions**. You get 5 questions you can ask at the end of the interview,
     each with a topic above it (for example "Tech stack" or "Team").

4. Wait a few seconds while "Asking the AI..." is shown.

Above the results, a gray line shows what they were made for, for example
*Generated for: Senior Backend Developer · openai/gpt-5-mini*. If you change the
role or level later, click the button again to get new questions.

### How to practice

- Answer each question out loud, or write your answer down, before you move on.
- Use the **STAR** method for experience questions: **S**ituation, **T**ask,
  **A**ction, **R**esult.
- Read the green **Interviewer tip** under the questions.
- Click the button again for a fresh set of questions.

---

## 4. JD Analyzer: understand a job posting

Use this page when you have a concrete job posting (JD = job description). The
page has three steps, one card each.

### Step 1: Paste the job description

Choose how you want to add the posting with the switch at the top of the card:
**📝 Text** or **🖼️ Screenshot**.

#### Option A: Text

1. Copy the whole posting from the job site: title, company, tasks and
   requirements.
2. Paste it into the big text box.
3. The counter under the box shows how many characters you have. You need **at
   least 200** and can paste **up to 15,000**.
4. Click **Analyze job description**.

#### Option B: Screenshots

Good for postings you can't copy as text (for example in an app or a PDF that
doesn't allow copying).

1. Take a screenshot of the posting. On Windows: press **Win+Shift+S** and
   select the area.
2. **Click the paste box** ("Click here, then press Ctrl+V"), then press
   **Ctrl+V**. You can also right-click it and choose **Paste**.
   Or use the **upload** field next to it to choose image files from your
   computer.
3. A long posting can be split into several screenshots, for example one with
   the title and one with the tasks. Add them **in reading order**: the
   numbers under the thumbnails show the order in which they are read.
4. To fix a mistake, click **Remove 1**, **Remove 2**, ... under a thumbnail,
   or **Remove all**.
5. Click **Process screenshot** (or **Process 3 screenshots** etc.).

The app first reads the text from your screenshots, then analyzes it. When it's
done, it switches to the **Text** view and shows the text it read, with the note
"Text read from ... Check it below." Read through it: if the app misread a word,
correct it in the text box and click **Analyze job description** again.

**Screenshot limits:**

| Rule | Limit |
|---|---|
| File types | PNG, JPG, WebP |
| Size of one screenshot | up to 5 MB |
| Number of screenshots per posting | up to 5 |
| All screenshots together | up to 15 MB |

The same screenshot is only added once, even if you paste it twice.

### Step 2: Review role and skills

After the analysis, this card shows:

- **A status bar** (dark line at the top): where the text came from (pasted
  text or the number of screenshots), the AI model used, and how many safety
  checks are on. Hover over the green or amber badge to see them listed.
- **Job title @ Company**, plus the type of job and work mode if the posting
  says so (for example *Full-time | Hybrid*).
- **Three tiles:**
  - **Seniority (inferred)**: the level the AI thinks the job is, with a short
    reason under it. Postings often don't say it directly, so the AI judges it
    from the tasks and the years of experience asked for.
  - **Role focus**: for example Backend or DevOps, with a reason.
  - **Location** and **work mode** (remote, hybrid, on-site).
- **Required skills** in three groups: **Tech stack**, **Concepts & domain**
  and **Soft skills**.
  - **Green** tags = required.
  - **Gray** tags under "Nice to have" = optional.
- **Other requirements**, such as a degree, languages or a driving licence.

"Not stated" or "Not detected" means the posting doesn't say it.

If you change the text in step 1 afterwards, a yellow note reminds you to click
**Analyze job description** again. Until then, step 2 still shows the old
result.

### Step 3: Your interview prep plan

Coming soon: a prep plan for this job, with the topics to focus on and your next
steps.

---

## 5. Coming soon

| Tool | What it will do |
|---|---|
| ✍️ **Intro Polisher** | Turn your "tell me about yourself" answer into a clear, confident pitch. |
| 🎯 **Resume Matcher** | Upload your resume and see how well it covers the skills a job asks for, as a percentage. |

Their pages already exist in the menu and say "This tool is coming soon".

---

## 6. AI settings (sidebar)

The dark panel on the left sets how the AI works. The settings apply to **all
pages** and stay when you switch pages. If you don't want to change anything,
the defaults are fine.

| Setting | What it does | Default |
|---|---|---|
| **Model** | Which AI model answers. The prices next to each name are in US dollars per 1 million tokens (input / output); a token is roughly ¾ of a word. | GPT-5 mini |
| **Temperature** | Low (e.g. 0.2) = focused, similar answers each time. High (e.g. 1.2) = more varied and creative. Grayed out for models that don't use it; you then see "This model ignores temperature". | 0.7 |
| **Max tokens** | The longest reply allowed. GPT-5 models also count their hidden "thinking" here, so very low values cut the reply off. | 4000 |

Available models: GPT-5 mini, GPT-5 nano, GPT-4.1 mini, GPT-4o mini, Gemini 2.5
Flash, Claude Haiku 4.5.

Tips:

- If you get the message that the reply was cut off, raise **Max tokens**
  (e.g. to 8000).
- For the same questions to come out more varied, raise the **Temperature**
  (only for models that support it).
- Cheaper models (GPT-5 nano, GPT-4o mini) are fine for trying things out.

---

## 7. Limits and safety

The app has safety checks that protect you and keep costs under control:

- **Input checks.** Texts that are too short or too long, and files that are
  too big or not real images, are refused **before** anything is sent to the
  AI. You see the reason at once.
- **IT interviews only.** The app only helps with interview and job
  application preparation for IT and tech jobs. Other requests (general chat,
  homework, recipes, jobs outside IT such as nursing or sales) are refused with
  a short message saying what the app can do instead.
- **Your text is treated as text.** If a job posting contains instructions
  such as "ignore your rules", the AI treats them as part of the posting and
  doesn't follow them.
- **Limit of 10 AI calls per minute.** Each "Generate" or "Analyze" click is one
  call. **Process screenshots** counts as **two** (one to read the
  screenshots, one to analyze the text). If you reach the limit, the message
  tells you how many seconds to wait.

**Your data.** The texts and screenshots you send are passed to an external AI
service to create the answer. Leave out personal details the task doesn't need,
such as your address or phone number.

---

## 8. Messages and what to do

| Message (example) | What it means | What to do |
|---|---|---|
| *The job description is too short (120 characters, at least 200 needed).* | Not enough text to analyze. | Paste the whole posting, including tasks and requirements. |
| *The job description is too long (...).* | More than 15,000 characters. | Remove parts that aren't about the job (company history, legal text). |
| *No image in the clipboard. Copy a screenshot first.* | You pressed Ctrl+V without a picture copied. | Take a screenshot (Win+Shift+S), then paste again. |
| *Screenshot 2 is too big (...).* / *Screenshot 1 is not a PNG, JPG or WebP image.* | That file doesn't fit the limits. | Use a smaller area, or save the picture as PNG or JPG. |
| *Too many screenshots (...)* / *The screenshots are too big together (...)* | More than 5 screenshots or 15 MB. | Remove some, or take fewer, larger screenshots. |
| *Too many requests: at most 10 AI calls per 60 seconds. Please wait 23 seconds.* | You hit the per-minute limit. | Wait the given time, then click again. |
| A short note that the request is out of scope | The request isn't about IT interview preparation. | Use a posting or role from IT and tech. |
| *Could not generate questions: ...* / *Could not analyze the job description: ...* | The AI call failed (network, service busy, reply cut off, ...). | Try again. If the message says the reply was cut off, raise **Max tokens**. Otherwise try another model. |

---

## 9. Tips

- **Start with the JD Analyzer** when you have a real posting: it shows which
  skills matter most. Then practice those topics in **Role Q&A**.
- **Paste the full posting.** The more of it the AI sees, the better the
  seniority and skill results.
- **Check the text read from screenshots** before you rely on the analysis.
- **Prepare 2–3 reverse questions** for every interview: they show real
  interest in the job.
- **Copy what you want to keep.** Results are lost when you reload the browser
  tab.
