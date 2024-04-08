import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import ttkbootstrap as tb
import json

class Task():
    def __init__(self, info: str, deadline = None):
        self.info = info
        self.deadline = deadline
        self.completed = "In Progress"
        self.subtasks = {}
    def complete_task_object(self):
        self.info = '\u0336'.join(self.info) + '\u0336'
        self.deadline = '\u0336'.join(self.deadline) + '\u0336'
        self.completed = "Done"
    def complete_subtask(self, subtask_info):
        self.subtasks['\u0336'.join(subtask_info) + '\u0336'] = self.subtasks[subtask_info]
        del self.subtasks[subtask_info]

        self.subtasks['\u0336'.join(subtask_info) + '\u0336'].complete_task_object()
    def add_subtask(self, subtask: "Task"):
        self.subtasks[subtask.return_fields()[0]] = subtask
    def remove_subtask(self, subtask_info: str):
        del self.subtasks[subtask_info]
    def change_task_deadline(self, new_deadline):
        self.deadline = new_deadline
    def change_subtask_deadline(self, subtask_info: str, new_deadline):
        self.subtasks[subtask_info].change_task_deadline(new_deadline)
    def return_fields(self) -> list:
        return [self.info, self.deadline, self.completed]
    def return_subtasks(self) -> dict:
        return self.subtasks
    def return_subtask_fields(self, subtask_info: str) -> list:
        return self.subtasks[subtask_info].return_fields()
    def return_subtasks_as_dict(self) -> dict:
        as_dict = self.subtasks
        for key in as_dict.keys():
            if type(as_dict[key]) != dict:
                as_dict[key] = as_dict[key].__dict__

        return as_dict
    def load_fields_from_dict(self, fields_as_dict: dict):
        self.info = fields_as_dict['info']
        self.deadline = fields_as_dict['deadline']
        self.completed = fields_as_dict['completed']

        for subtask in fields_as_dict['subtasks'].items():
            self.subtasks[subtask[0]] = Task("")
            self.subtasks[subtask[0]].load_fields_from_dict(subtask[1])
class ToDoList():
    def __init__(self, root, saving_file: str):
        self.root = root
        self.saving_file = saving_file
        self.task_dict = {}
        self.root.title("Task Manager Application")
        self.root.geometry("510x450")

        self.task_info_entry = tk.Entry(root, width=30, font=('Cambria', 12))
        self.task_info_entry.place(x=10, y=30)
        self.task_entry_comment = "Enter task/subtask..."
        self.task_info_entry.bind("<FocusIn>", self.task_entry_clear_placeholder)
        self.task_info_entry.bind("<FocusOut>", self.task_entry_restore_placeholder)

        self.task_entry_restore_placeholder(None)

        self.date_entry = tb.DateEntry(root, width=11, bootstyle="secondary", firstweekday=0)
        self.date_entry.place(x=360, y=30)

        self.task_add_button = tk.Button(root, text="ADD Task", command=self.add_task, font=('Cambria', 12))
        self.task_add_button.place(x=20, y=80, width=140)

        self.subtask_add_button = tk.Button(root, text="ADD Subtask", command=self.add_subtask, font=('Cambria', 12))
        self.subtask_add_button.place(x=170, y=80, width=140)

        self.deadline_change_button = tk.Button(root, text="CHANGE Deadline", command=self.change_deadline, font=('Cambria', 12))
        self.deadline_change_button.place(x=320, y=80, width=170)

        self.task_complete_button = tk.Button(root, text="COMPLETE", command=self.complete_task, font=('Cambria', 12))
        self.task_complete_button.place(x=20, y=400, width=140)

        self.task_remove_button = tk.Button(root, text="REMOVE", command=self.remove_task, font=('Cambria', 12))
        self.task_remove_button.place(x=170, y=400, width=140)

        self.task_exit_button = tk.Button(root, text="Exit", command=self.save_data, font=('Cambria', 12))
        self.task_exit_button.place(x=410, y=400, width=80)

        self.task_tree = ttk.Treeview(columns=("Deadline", "Status"), selectmode=tk.BROWSE)
        self.task_tree.place(x=10, y=140, width=490)

        self.task_tree.column("#0", width=270, stretch=NO)
        self.task_tree.column("Deadline", anchor=CENTER, width=110)
        self.task_tree.column("Status", anchor=CENTER, width=110)

        self.task_tree.heading("#0", text="Task info", anchor=CENTER)
        self.task_tree.heading("Deadline", text="Deadline", anchor=CENTER)
        self.task_tree.heading("Status", text="Status", anchor=CENTER)

        self.load_saved_data()
    def load_saved_data(self):
        with open(self.saving_file, 'r') as data_file:
           try:
               data = json.loads(data_file.read())

               for task in data.items():
                   self.task_dict[task[0]] = Task("")
                   self.task_dict[task[0]].load_fields_from_dict(task[1])

               for task in self.task_dict.values():
                   inserted_task = self.task_tree.insert(parent='', index=tk.END, text=task.return_fields()[0],
                                                         values=task.return_fields()[1:3])
                   if task.return_subtasks():
                      for subtask in task.return_subtasks().values():
                         self.task_tree.insert(parent=inserted_task, index=tk.END, text=subtask.return_fields()[0],
                                               values=subtask.return_fields()[1:3])
           except Exception as e:
               self.task_dict = {}
    def add_task(self):
        task_info = self.task_info_entry.get()
        task_deadline = self.date_entry.entry.get()

        if (task_info and task_info != self.task_entry_comment) and task_deadline:
            if not self.task_dict.get(task_info):
                self.task_dict[task_info] = Task(task_info, task_deadline)

                self.task_tree.insert(parent='', index=tk.END, text=task_info,
                                      values=(task_deadline, "In Progress"))
            else:
                messagebox.showwarning("Warning", "This item already exists")
            self.task_info_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Enter task information & deadline before submission")
    def add_subtask(self):
        subtask_info = self.task_info_entry.get()
        subtask_deadline = self.date_entry.entry.get()

        selected_id = self.task_tree.selection()
        if (subtask_info and subtask_info != self.task_entry_comment) and subtask_deadline and selected_id:
            selected_item_info = self.task_tree.item(selected_id[0])["text"]

            if selected_item_info in self.task_dict.keys() and self.task_dict[selected_item_info].return_fields()[-1] != "Done":

                if not self.task_dict[selected_item_info].return_subtasks().get(subtask_info) and not self.task_dict.get(subtask_info):
                    self.task_dict[self.task_tree.item(selected_id[0], option="text")].add_subtask(Task(subtask_info, subtask_deadline))
                    self.task_tree.insert(parent=selected_id[0], index=tk.END, text=subtask_info,
                                          values=(subtask_deadline, "In Progress"))
                else:
                    messagebox.showwarning("Warning", "This item already exists")
                self.task_info_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Warning", "Subtasks could not be added to this item")
        else:
            messagebox.showwarning("Warning", "Enter subtask information & deadline, select the parent task")
    def complete_task(self):
        selected_id = self.task_tree.selection()
        if selected_id:
            selected_item_info = self.task_tree.item(selected_id[0])["text"]

            if selected_item_info not in self.task_dict.keys():
                parent_id = self.task_tree.parent(selected_id[0])
                parent_task_info = self.task_tree.item(parent_id)["text"]
                selected_subtask_fields = self.task_dict[parent_task_info].return_subtask_fields(selected_item_info)

                if selected_subtask_fields[-1] != "Done":
                    self.task_dict[self.task_tree.item(parent_id)["text"]].complete_subtask(selected_item_info)
                    self.task_tree.item(selected_id[0], text='\u0336'.join(selected_item_info) + '\u0336',
                                        values=self.task_dict[parent_task_info].
                                        return_subtask_fields('\u0336'.join(selected_item_info) + '\u0336')[1:3])
                else:
                    messagebox.showwarning("Warning", "Selected item has already been completed")

            elif self.task_dict[selected_item_info].return_fields()[-1] != "Done":
                has_uncompleted_subtasks = False
                for subtask in self.task_dict[selected_item_info].return_subtasks().values():
                    if subtask.return_fields()[-1] == "Done":
                        pass
                    else:
                        has_uncompleted_subtasks = True
                        break

                if not has_uncompleted_subtasks:
                    self.task_dict[selected_item_info].complete_task_object()
                    self.task_dict['\u0336'.join(selected_item_info) + '\u0336'] = self.task_dict[selected_item_info]
                    del self.task_dict[selected_item_info]

                    self.task_tree.item(selected_id[0], text='\u0336'.join(selected_item_info) + '\u0336',
                                        values=(self.task_dict['\u0336'.join(selected_item_info) + '\u0336']
                                        .return_fields()[1:3]))
                else:
                    messagebox.showwarning("Warning", "This task has uncompleted subtasks")
            else:
                messagebox.showwarning("Warning", "Selected item has been already completed")
        else:
            messagebox.showwarning("Warning", "Select an item before completion")
    def change_deadline(self):
        selected_id = self.task_tree.selection()
        if selected_id:
            selected_item_info = self.task_tree.item(selected_id[0])["text"]

            if selected_item_info in self.task_dict.keys():
                selected_item_fields = self.task_dict[selected_item_info].return_fields()

                if selected_item_fields[-1] != "Done":
                    self.task_dict[selected_item_info].change_task_deadline(self.date_entry.entry.get())
                    self.task_tree.item(selected_id[0], values=(self.date_entry.entry.get(), selected_item_fields[-1]))
                else:
                    messagebox.showwarning("Warning", "Deadline could not be changed on this item")
            else:
                parent_id = self.task_tree.parent(selected_id[0])
                parent_task_info = self.task_tree.item(parent_id)["text"]
                selected_subtask_fields = self.task_dict[parent_task_info].return_subtask_fields(selected_item_info)

                if selected_subtask_fields[-1] != "Done":
                    self.task_dict[parent_task_info].change_subtask_deadline(selected_item_info, self.date_entry.entry.get())
                    self.task_tree.item(selected_id[0], values=(self.date_entry.entry.get(), selected_subtask_fields[-1]))
                else:
                    messagebox.showwarning("Warning", "Deadline could not be changed on this item")
        else:
            messagebox.showwarning("Warning", "Select an item to change deadline on")
    def remove_task(self):
        selected_id = self.task_tree.selection()
        if selected_id:
            selected_item_info = self.task_tree.item(selected_id[0])["text"]
            if selected_item_info in self.task_dict.keys():
                del self.task_dict[selected_item_info]
            else:
                parent_id = self.task_tree.parent(selected_id[0])
                self.task_dict[self.task_tree.item(parent_id)["text"]].remove_subtask(selected_item_info)

            self.task_tree.delete(selected_id[0])
        else:
            messagebox.showwarning("Warning", "Select an item before removal")
    def task_entry_clear_placeholder(self, event):
        if self.task_info_entry.get() == self.task_entry_comment:
            self.task_info_entry.delete(0, tk.END)
    def task_entry_restore_placeholder(self, event):
        if self.task_info_entry.get() == "":
            self.task_info_entry.insert(0, self.task_entry_comment)
    def return_as_dict(self) -> dict:
        as_dict = self.task_dict
        for key in as_dict.keys():
            if type(as_dict[key]) != dict:
                subtasks_as_dict = as_dict[key].return_subtasks_as_dict()
                as_dict[key] = as_dict[key].__dict__
                as_dict[key]["subtasks"] = subtasks_as_dict

        return as_dict
    def save_data(self):
        with open(self.saving_file, "w") as file:
            data = json.dumps(self.return_as_dict())
            file.write(data)
        self.root.destroy()

if __name__ == "__main__":
    root = tb.Window(themename="vapor")
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Cambria", 12))

    toDoList = ToDoList(root, "saving_file")
    root.mainloop()
