# Text-to-SQL Agent

<a href="#">
  <picture>
    <source
      media="(prefers-color-scheme: dark)"
      srcset="https://cdn.firebasestudio.dev/btn/try_light_20.svg">
    <source
      media="(prefers-color-scheme: light)"
      srcset="https://cdn.firebasestudio.dev/btn/try_dark_20.svg">
    <img
      height="20"
      alt="Try Online"
      src="https://cdn.firebasestudio.dev/btn/try_blue_20.svg">
  </picture>
</a>

<div style="text-align: right;">
  <details>
    <summary>🌐 Language</summary>
    <div style="text-align: center;">
      English | 简体中文 | 繁體中文 | 日本語 | 한국어 | हिन्दी | ไทย | Français |
      Deutsch | Español | Italiano | Русский | Português | Nederlands | Polski |
      العربية | فارسی | Türkçe | Tiếng Việt | Bahasa Indonesia
    </div>
  </details>
</div>

This repository contains a **Text-to-SQL Agent** that converts natural-language questions into SQL queries and executes them securely on **MySQL** or **Google Cloud SQL** using the **Google ADK (Agents Framework)** and **Gemini models**.

It enables analysts, developers, and support teams to query databases conversationally — without writing SQL.

---

## ✨ Features

- 🧠 **Natural Language → SQL Conversion**  
  Converts user questions like:  
  _“Show top 5 employees by salary”_  
  into valid MySQL SQL.

- 🛢️ **MySQL / Cloud SQL Execution**  
  Executes generated SQL using Cloud SQL Connector or local PyMySQL.

- 🔒 **SQL Safety Layer**  
  - Blocks destructive SQL (`DROP`, `DELETE`, `ALTER`, etc.)
  - Limits queries with automatic `LIMIT`
  - Sanitizes input & prevents multi-statements

- 📊 **Insight Extraction**  
  Can summarize results and highlight insights.

- 🔍 **Schema Discovery**  
  Agent uses:  
  - `SHOW TABLES`  
  - `DESCRIBE table_name`  
  to explore database structure.

---

## 🧠 Architecture

```mermaid
flowchart TD
    User[User Query] --> Agent[Gemini Agent]
    Agent --> SQLGen[Natural Language → SQL Generator]
    SQLGen --> Validator[SQL Safety Validator]
    Validator -->|Approved| Tool[run_mysql_query Tool]
    Validator -->|Blocked| Error[Return Safe Error Message]

    Tool --> CloudSQL[(MySQL / Cloud SQL)]
    CloudSQL --> Tool
    Tool --> Agent
    Agent --> User[Results + Insights]
d

