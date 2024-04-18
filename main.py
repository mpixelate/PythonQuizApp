import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import csv
import random
from functools import partial


class Colors:
    bg = "#7DCDF2"
    radiobutton_bg = "light blue"
    question_bg = "#289EF5"
    correct_answer = "#4dff4d"
    wrong_answer = "#ff6666"
    correct_answer2 = "#ffff4d"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("480x650")
        self.title("Quiz game about Python")

        questions_list = []
        topics = set()
        try:
            with open("questions.csv") as question_file:
                questions = csv.DictReader(question_file, delimiter=";")
                for row in questions:
                    questions_list.append(row)
                    topics.add(questions_list[-1]["topic"])
                topics = list(topics)

        except (FileNotFoundError) as e:
            messagebox.showerror(title="Error", message="The file 'questions.csv' that contains all questions is not found.")
            self.destroy()
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        frame = MainMenuFrame(container, self)
        self.frames[MainMenuFrame] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        frame = QuizFrame(container, self, questions_list)
        self.frames[QuizFrame] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        frame = InstructionFrame(container, self)
        self.frames[InstructionFrame] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(MainMenuFrame)

        self.mainloop()


    def show_frame(self, frame_i: tk.Frame, **kwargs):
        frame = self.frames[frame_i]
        frame.tkraise()
        frame.update_content(**kwargs)


class MainMenuFrame(tk.Frame):
    def __init__(self, parent, controller: App, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs, bg=Colors.bg)
        
        self.controller = controller
        container = tk.Frame(self, bg="yellow")
        container.pack(expand=1)

        btn_start_quiz = tk.Button(container, text="Start", padx=10, pady=10, command=lambda: self.controller.show_frame(QuizFrame))
        btn_start_quiz.pack(expand=1, fill="x")

        btn_view_instructions = tk.Button(container, text="View instructions", padx=10, pady=10, command=lambda: self.controller.show_frame(InstructionFrame))
        btn_view_instructions.pack(expand=1, fill="x")

        btn_exit_game = tk.Button(container, text="Exit the game", padx=10, pady=10, command=self.controller.destroy)
        btn_exit_game.pack(expand=1, fill="x")
    

    def update_content(self, **kwargs):
        pass


class QuizFrame(tk.Frame):
    def __init__(self, parent, controller: App, questions_list: list):
        tk.Frame.__init__(self, parent, bg=Colors.bg)

        self.finished = False
        self.controller = controller
        self.questions_list = questions_list

        self.container = tk.Frame(self, borderwidth=2)
        self.container.pack(expand=1, padx=40, pady=40)

        self.timer_frame = tk.Frame(self.container)
        self.timer_frame.pack(fill="x")

        self.lbl_timer = tk.Label(self.timer_frame, text="lasts 100 s")
        self.lbl_timer.pack(padx=5, pady=5, fill="x", side="left")
        self.pbar_timer = ttk.Progressbar(self.timer_frame, orient="horizontal", maximum=60, value=40, style="primary.Striped.Horizontal.TProgressbar")
        self.pbar_timer.pack(padx=5, pady=5, expand=1, fill="x", side="left")
        
        self.lbl_header = tk.Label(self.container, text="Choose a correct option", padx=5, pady=20)
        self.lbl_header.pack()

        self.question_box_frame = tk.Frame(self.container)
        self.question_box_frame.pack()

        self.questions_cnt = 10

        self.questions = [QuestionFrame(self, self) for i in range(self.questions_cnt)]
        for i in range(self.questions_cnt):
            self.questions[i] = QuestionFrame(self.question_box_frame, self)
            self.questions[i].grid(row=0, column=0, sticky="nsew")

        self.btn_previous = tk.Button(self.container, text="Previous", command=self.switch_to_previous_question, padx=10, pady=10)
        self.btn_previous.pack(side="left", expand=1, fill="x")
        self.btn_back2menu = tk.Button(self.container, text="Back to menu", command=self.back_to_menu_command, padx=10, pady=10)
        self.btn_back2menu.pack(side="left", expand=1, fill="x")

        # all_questions or current_question
        self.btn_all_questions = tk.Button(self.container, text="All questions", command=self.show_all_question, padx=10, pady=10)
        self.btn_all_questions.pack(side="left", expand=1, fill="x")
        self.btn_next = tk.Button(self.container, text="Next", command=self.switch_to_next_question, padx=10, pady=10)
        self.btn_next.pack(side="left", expand=1, fill="x")

        self.all_questions = AllQuestionsFrame(self.question_box_frame, self, self.questions)
        self.all_questions.grid(row=0, column=0, sticky="nsew")


        self.current_question = 0
        self.show_nth_question(self.current_question)
    

    def switch_to_next_question(self):
        if self.current_question < self.questions_cnt - 1:
            self.current_question += 1
            self.show_nth_question(self.current_question)
        elif self.current_question == self.questions_cnt - 1:
            answer = messagebox.askyesno(title="Confirmation", message="Are you sure you want to finish the quiz? You will no longer be able to change your answers.")
            if answer:
                self.finish_quiz()
    

    def back_to_menu_command(self):
        if self.finished:
            answer = messagebox.askyesno(title="Confirmation", message="Are you sure you want to exit the quiz?")
        else:
            answer = messagebox.askyesno(title="Confirmation", message="Are you sure you want to exit the quiz? Your progress will not be saved.")
        if answer:
            self.controller.show_frame(MainMenuFrame)


    def show_all_question(self):
        if self.finished == True:
            self.all_questions.show_result()
        else:
            self.all_questions.update()

        if self.finished:
            self.lbl_header.config(text=f"Total score {self.get_total_score()}/{self.questions_cnt}")
        else:
            self.lbl_header.config(text="All questions:")
        self.btn_all_questions.config(text="Current question", command=lambda: self.show_nth_question(self.current_question))
        self.all_questions.tkraise()


    def switch_to_previous_question(self):
        if self.current_question > 0:
            self.current_question -= 1
            self.show_nth_question(self.current_question)
    
    
    def show_nth_question(self, ind: int):
        self.current_question = ind

        self.lbl_header.config(text="Choose a correct option")

        if self.finished:
            self.btn_all_questions.config(text="Overall result", command=self.show_all_question)
        else:
            self.btn_all_questions.config(text="All questions", command=self.show_all_question)

        if self.current_question == self.questions_cnt - 1:
            if self.finished:
                self.btn_next.config(text="", command=lambda: print(end=""))
            else:
                self.btn_next.config(text="Finish")
        else:
            self.btn_next.config(text="Next", command=self.switch_to_next_question)
        self.questions[ind].tkraise()


    def update_content(self, **kwargs):
        self.show_nth_question(0)
        self.generate_quiz()
        self.finished = False
    

    def generate_quiz(self):
        random.shuffle(self.questions_list)

        for i in range(self.questions_cnt):
            self.questions[i].restart()
            self.questions[i].set_question_text(str(i + 1) + ". " + self.questions_list[i]["question"])
            self.questions[i].set_options(self.questions_list[i]["correct_answer"], [self.questions_list[i]["answer2"],
                                                                                     self.questions_list[i]["answer3"],
                                                                                     self.questions_list[i]["answer4"]])
        
        self.start_timer(60)
    

    def finish_quiz(self):
        self.finished = True
        self.lbl_header.config(text=f"Total score {self.get_total_score()}/{self.questions_cnt}")
        for i in range(self.questions_cnt):
            self.questions[i].freeze()
        self.show_all_question()
        self.stop_timer()


    def get_total_score(self):
        cnt = 0
        for i in range(self.questions_cnt):
            if self.questions[i].correct_answer_ind == int(self.questions[i].selected_option.get()):
                cnt += 1
        return cnt


    def start_timer(self, end_time: int):
        self.pbar_timer.config(value=end_time, maximum=end_time)
        self.lbl_timer.config(text=str(end_time) + "s")
        self.time = end_time
        self.end_time = 0
        self.after(1000, self.upd)
    

    def upd(self):
        self.time -= 1
        self.pbar_timer.config(value=self.time)
        self.lbl_timer.config(text=str(self.time) + "s")
        if self.time > 0:
            self.id = self.after(1000, self.upd)
        else:
            self.finish_quiz()
            self.show_all_question()
    

    def stop_timer(self):
        self.after_cancel(self.id)


class QuestionFrame(tk.Frame):
    def __init__(self, parent, controller: QuizFrame, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs, bg=Colors.question_bg)
        self.lbl_question = tk.Label(self, text=f"Question {random.randint(0, controller.questions_cnt)}", padx=20, pady=20, justify="left", wraplength=300, bg=Colors.question_bg, font=(15))
        self.lbl_question.pack()

        self.selected_option = tk.StringVar(value=-1)
        
        self.options = [tk.Radiobutton() for i in range(4)]

        for i in range(4):
            self.options[i] = tk.Radiobutton(self, value=i, variable=self.selected_option, justify="left", wraplength=300, bg=Colors.radiobutton_bg, indicator=False, highlightbackground=Colors.radiobutton_bg)
            self.options[i].pack(expand=1, fill="both")
    

    def set_question_text(self, text: str):
        self.question_text = text
        self.lbl_question.config(text=text)
    

    def set_options(self, correct_answer: str, other_options: list[str]):
        self.correct_answer_ind = random.randint(0, 3)
        self.selected_option = tk.StringVar(value=-1)
        self.options[self.correct_answer_ind].config(text=correct_answer, variable=self.selected_option, value=self.correct_answer_ind)
        random.shuffle(other_options)

        j = 0
        for i in range(4):
            if i != self.correct_answer_ind:
                self.options[i].config(text=other_options[j], variable=self.selected_option, value=i)
                j += 1
    

    def freeze(self):
        for i in range(4):
            self.options[i].config(state="disabled")
        
        if self.correct_answer_ind == int(self.selected_option.get()):
            self.options[self.correct_answer_ind].config(background=Colors.correct_answer)
        else:
            self.options[self.correct_answer_ind].config(background=Colors.correct_answer2)


    def restart(self):
        for i in range(4):
            self.options[i].config(state="active", bg="white")
            self.selected_option.set(value=-1)


class AllQuestionsFrame(tk.Frame):
    def __init__(self, parent, controller: QuizFrame, questions: list[QuestionFrame], **kwargs):
        super().__init__(parent, bg=Colors.question_bg, **kwargs)
        self.controller = controller
        self.container = tk.Frame(self)
        self.container.pack(expand=1)
        self.questions = questions
        self.lbl_questions = [tk.Label() for i in range(controller.questions_cnt)]
        self.lbl_questions_status = [tk.Label() for i in range(controller.questions_cnt)]
        self.btn_questions_open = [tk.Button() for i in range(controller.questions_cnt)]

        grid_table = tk.Frame(self.container, padx=3, pady=3)
        grid_table.pack(fill="both")

        cell_config = {"padx": 3, "pady": 3, "borderwidth": 3}
        for i in range(controller.questions_cnt):
            self.lbl_questions[i] = tk.Label(grid_table, text="Random text", **cell_config, justify="left", anchor="w", wraplength=250)
            self.lbl_questions[i].grid(row=i, column=0, sticky="nesw")

            self.lbl_questions_status[i] = tk.Label(grid_table, text="unanswered", **cell_config)
            self.lbl_questions_status[i].grid(row=i, column=1, sticky="we")

            self.btn_questions_open[i] = tk.Button(grid_table, text="Open", **cell_config, command=partial(controller.show_nth_question, i))
            self.btn_questions_open[i].grid(row=i, column=2)
    

    def update(self):
        for i in range(self.controller.questions_cnt):
            self.lbl_questions[i].config(text=str(i + 1) + ". " + self.questions[i].question_text)
            self.lbl_questions[i].config(bg="white")
            self.lbl_questions_status[i].config(bg="white")
            self.btn_questions_open[i].config(bg="white")
            if int(self.questions[i].selected_option.get()) == -1:
                self.lbl_questions_status[i].config(text="Unanswered")
            else:
                self.lbl_questions_status[i].config(text="Answered")
    

    def show_result(self):
        for i in range(self.controller.questions_cnt):
            self.lbl_questions[i].config(text=self.questions[i].question_text)
            if int(self.questions[i].selected_option.get()) == -1:
                self.lbl_questions_status[i].config(text="Unanswered")

                self.lbl_questions[i].config(bg=Colors.wrong_answer)
                self.lbl_questions_status[i].config(bg=Colors.wrong_answer)
                self.btn_questions_open[i].config(bg=Colors.wrong_answer)

            elif int(self.questions[i].selected_option.get()) == self.questions[i].correct_answer_ind:
                self.lbl_questions_status[i].config(text="Correct")

                self.lbl_questions[i].config(bg=Colors.correct_answer)
                self.lbl_questions_status[i].config(bg=Colors.correct_answer)
                self.btn_questions_open[i].config(bg=Colors.correct_answer)
            else:
                self.lbl_questions_status[i].config(text="Wrong")

                self.lbl_questions[i].config(bg=Colors.wrong_answer)
                self.lbl_questions_status[i].config(bg=Colors.wrong_answer)
                self.btn_questions_open[i].config(bg=Colors.wrong_answer)


class InstructionFrame(tk.Frame):
    def __init__(self, parent, controller: App):
        tk.Frame.__init__(self, parent, bg=Colors.bg)
        self.container = tk.Frame(self, padx=20, pady=20)
        self.container.pack(expand=1)
        text = ""
        try:
            with open("instructions.txt") as file:
                for line in file:
                    text += line
        except (FileNotFoundError) as e:
            messagebox.showerror(title="Error", message="The file 'instructions.txt' that contains instructions is not found.")
            self.destroy()
        lbl_instructions = tk.Label(self.container, text=text, wraplength=350, justify="left")
        lbl_instructions.pack()

        tk.Button(self.container, text="Back to menu", command=lambda: controller.show_frame(MainMenuFrame), padx=10, pady=10).pack(side="bottom")
    

    def update_content(self, **kwargs):
        pass


class ResultQuizFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
    

    def update_content(self, **kwargs):
        pass


if __name__ == "__main__":
    app = App()