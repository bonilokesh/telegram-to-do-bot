# ✅ Telegram To-Do List Bot

A simple Telegram bot that allows users to manage their to-do lists directly through Telegram.

## 📌 Features

- Add tasks to your to-do list
- View current tasks
- Mark tasks as done
- Delete completed or specific tasks
- Persistent storage of tasks per user

## link to the bot
https://t.me/task2003bot


###  Database Schema

This bot uses a **MySQL** database named `task_bot` with a single table named `tasks`. Below is the schema used:

## ⚠️ Note: You must manually create the task_bot database in your MySQL server and run the below CREATE TABLE query before using the bot. Make sure your database connection settings are correctly configured in your code.

```sql
CREATE TABLE tasks (
    id INT PRIMARY KEY,
    user_id BIGINT,
    task_description VARCHAR(255),
    due_date DATETIME,
    created_at DATETIME,
    completed TINYINT(1)
);


