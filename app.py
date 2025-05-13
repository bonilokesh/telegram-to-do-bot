from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from db_config import get_connection
from dotenv import load_dotenv
scheduler = AsyncIOScheduler()
scheduler.start()

load_dotenv()
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use /addtask <task> <YYYY-MM-DD_HH:MM> to set a reminder.")

async def addtask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        user_id = update.effective_user.id
        task_description = ' '.join(args[:-1])
        due_time = datetime.strptime(args[-1], "%Y-%m-%d_%H:%M")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (user_id, task_description, due_date, created_at, completed)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, task_description, due_time, datetime.now(), False))
        conn.commit()
        conn.close()

        scheduler.add_job(send_reminder, 'date', run_date=due_time, args=[user_id, task_description, context])

        await update.message.reply_text(f"Task saved and reminder scheduled!")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def send_reminder(user_id, task_description, context):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Fetch the task and check if it is not completed
        cursor.execute("""
            SELECT completed FROM tasks 
            WHERE user_id = %s AND task_description = %s
        """, (user_id, task_description))
        result = cursor.fetchone()

        if result and not result[0]:  # result[0] == completed flag
            await context.bot.send_message(chat_id=user_id, text=f" Reminder: {task_description}")
        else:
            print("Task is either not found or already completed. No reminder sent.")

    except Exception as e:
        print(f"Error sending reminder: {str(e)}")
    finally:
        conn.close()

    
   
async def showtasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        
        # Connect to the database and retrieve tasks for this user
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT task_description, due_date, completed FROM tasks WHERE user_id = %s", (user_id,))
        tasks = cursor.fetchall()
        conn.close()

        # If no tasks are found
        if not tasks:
            await update.message.reply_text("You have no tasks.")
            return

        # Format the tasks for display
        task_list = ""
        for task in tasks:
            task_description, due_date, completed = task
            completed_text = "✅ Completed" if completed else "❌ Pending"
            task_list += f"Task: {task_description}\nDue: {due_date}\nStatus: {completed_text}\n\n"

        await update.message.reply_text(task_list)
        
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def deletetask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) == 0:
            await update.message.reply_text("Please provide the task description to delete.")
            return

        task_description = ' '.join(args)
        user_id = update.effective_user.id

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM tasks
            WHERE user_id = %s AND task_description = %s
        """, (user_id, task_description))

        if cursor.rowcount == 0:
            await update.message.reply_text("No matching task found to delete.")
        else:
            conn.commit()
            await update.message.reply_text(f"Task '{task_description}' deleted 🗑️")

        conn.close()

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def markdone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) == 0:
            await update.message.reply_text("Please provide the task description to mark as done.")
            return

        task_description = ' '.join(args)
        user_id = update.effective_user.id

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE tasks
            SET completed = TRUE
            WHERE user_id = %s AND task_description = %s
        """, (user_id, task_description))

        if cursor.rowcount == 0:
            await update.message.reply_text("No matching task found to mark as completed.")
        else:
            conn.commit()
            await update.message.reply_text(f"Task '{task_description}' marked as completed ✅")

        conn.close()

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")



if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addtask", addtask))
    app.add_handler(CommandHandler("showtasks", showtasks))
    app.add_handler(CommandHandler("deletetask", deletetask))
    app.add_handler(CommandHandler("markdone", markdone))
    app.add_handler(CommandHandler("help", start))
    print("Bot is running...")
    app.run_polling()
