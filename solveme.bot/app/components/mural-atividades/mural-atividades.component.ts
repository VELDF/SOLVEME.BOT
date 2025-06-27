import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'; 
import { NgModule } from '@angular/core';

interface Task {
  title: string;
  date: string;
}

interface Column {
  title: string;
  tasks: Task[];
  filteredTasks: Task[];
}

@Component({
  selector: 'app-mural-atividades',
  imports: [CommonModule,FormsModule],
  templateUrl: './mural-atividades.component.html',
  styleUrl: './mural-atividades.component.css'
})

export class MuralAtividadesComponent {

  searchTerm = '';
  draggingTask?: Task;
  draggingFromCol?: number;

  columns: Column[] = [
    {
      title: 'Todas as tarefas',
      tasks: [
        { title: 'Criar endpoint de upload de documentos empresariais', date: '01/01/2025' },
        { title: 'Ajustar layout da fila de feedback de chamados', date: '01/01/2025' },
        { title: 'Enviar formulário de feedback', date: '01/01/2025' }
      ],
      filteredTasks: []
    },
    {
      title: 'A fazer',
      tasks: [
        { title: 'Ajustar layout da fila...', date: '12/01/2025' },
        { title: 'Criar canal no Slack/Discord', date: '14/01/2025' }
      ],
      filteredTasks: []
    },
    {
      title: 'Fazendo',
      tasks: [
        { title: 'Testar chatbot com permissão...', date: '14/01/2025' }
      ],
      filteredTasks: []
    },
    {
      title: 'Concluído',
      tasks: [],
      filteredTasks: []
    }
  ];

  constructor() {
    this.filterTasks();
  }

  filterTasks() {
    const term = this.searchTerm.toLowerCase();
    for (const col of this.columns) {
      col.filteredTasks = col.tasks.filter(task =>
        task.title.toLowerCase().includes(term)
      );
    }
  }

  onDragStart(event: DragEvent, colIndex: number, task: Task) {
    this.draggingTask = task;
    this.draggingFromCol = colIndex;
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
  }

  onDrop(event: DragEvent, targetColIndex: number) {
    if (
      this.draggingTask &&
      this.draggingFromCol !== undefined &&
      this.draggingFromCol !== targetColIndex
    ) {
      const fromTasks = this.columns[this.draggingFromCol].tasks;
      const toTasks = this.columns[targetColIndex].tasks;

      const index = fromTasks.indexOf(this.draggingTask);
      if (index > -1) {
        fromTasks.splice(index, 1);
        toTasks.push(this.draggingTask);
        this.filterTasks();
      }
    }

    this.draggingTask = undefined;
    this.draggingFromCol = undefined;
  }

  addTask(colIndex?: number) {
    const title = prompt('Nova tarefa:');
    if (title) {
      const task = { title, date: new Date().toLocaleDateString() };
      if (colIndex !== undefined) {
        this.columns[colIndex].tasks.push(task);
      } else {
        this.columns[0].tasks.push(task);
      }
      this.filterTasks();
    }
  }

  voltar() {
    window.history.back();
  }
}

 

