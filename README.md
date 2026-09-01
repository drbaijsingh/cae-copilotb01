# CAE Copilot — your own website

Three HTML files. No build step, no server, no dependencies, no database.
Put them anywhere that serves files and you have a working public website.

```
index.html      the landing page (start here)
copilot.html    Script Builder, Error Doctor, Setup Advisor, Materials reference
materials.html  FGM, laminate, sandwich, parametric study
.nojekyll       tells GitHub not to interfere with the files
```

The pages link to each other with plain relative paths, so the whole folder
works as-is — on a web host, on a USB stick, or by double-clicking `index.html`
on your own machine.

---

## Publish it free on GitHub Pages — about 10 minutes

This gives you **your own permanent URL**, something like
`https://baijns.github.io/cae-copilot/`. Anyone can open it. No login for
them, no Claude account, nothing to install. You own it.

### 1. Make a GitHub account
Go to <https://github.com> and sign up. Free. Choose your username carefully —
it becomes part of your URL, so `baijns` or `baijnathsingh` rather than
something you will regret on a business card.

### 2. Create a repository
Click **+** (top right) → **New repository**.

- **Repository name:** `cae-copilot`
- **Public** (this is required for free Pages hosting)
- Tick **Add a README file**
- Click **Create repository**

### 3. Upload these files
On the repository page: **Add file** → **Upload files**.

Drag in `index.html`, `copilot.html`, `materials.html` and `.nojekyll`.

> If your file manager hides `.nojekyll` because it starts with a dot, don't
> worry — the site works without it. It only prevents a rare GitHub quirk.

Scroll down, click **Commit changes**.

### 4. Turn on Pages
**Settings** (top of the repository) → **Pages** (left sidebar).

- Under *Source*, choose **Deploy from a branch**
- Branch: **main**, folder: **/ (root)**
- Click **Save**

Wait two or three minutes. Refresh the page and GitHub will show your live URL
at the top.

### 5. Test it properly
Open the URL **on your phone, on mobile data, not on wifi**. That proves it
works for someone who is not you and not on your network. If it loads there,
it loads for everyone.

---

## After it is live

**Put the URL everywhere.** Your LinkedIn headline and about section, your
email signature, your university profile page, the last slide of every talk
you give, and your CV.

**Updating is easy.** Edit a file, or upload a replacement with the same name.
GitHub redeploys in about a minute. No rebuild, no pipeline.

**Add a custom domain later if you want one.** `caecopilot.com` or similar
costs a few hundred rupees a year and points at the same files — Settings →
Pages → Custom domain. Do this only once people are actually using the tool.

---

## Get a DOI so the tool is citable

Once the repository exists, connect it to [Zenodo](https://zenodo.org):

1. Sign in to Zenodo with your GitHub account
2. Go to your Zenodo GitHub settings and switch **on** the `cae-copilot` repository
3. Back on GitHub: **Releases** → **Create a new release** → tag it `v1.0` → **Publish release**

Zenodo mints a DOI for that release automatically. From then on your students
and co-authors can cite the tool properly:

> Singh, B. N. (2026). *CAE Copilot: a validated semi-analytical toolkit for
> graded and layered plate vibroacoustics* (v1.0) [Software]. Zenodo.
> https://doi.org/10.5281/zenodo.XXXXXXX

That citation counts. It is a research output with a permanent identifier,
it goes in your CV and your promotion file, and it makes the tool something
other groups can build on and reference rather than just use.

---

## What to add to the repository next

Copy in the `validation/` folder from your archive. It is the evidence that
every number the tool produces has been checked against published reference
values — Leissa (1969) for the boundary conditions, classical plate theory for
the laminate route, limiting cases for the FGM homogenisation.

A tool that ships its own validation suite is in a different category from one
that does not. That folder is the reason a researcher will trust this enough
to use it in a paper.

---

Dr. Baij Nath Singh · Greater Noida
