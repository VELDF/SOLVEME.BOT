import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { QuillModule } from 'ngx-quill';
import { RouterModule } from '@angular/router';

interface Anotacao {
  titulo: string;
  texto: string;
  selecionada: boolean;
}

@Component({
  selector: 'app-bloco-notas',
  standalone: true,
  imports: [CommonModule, FormsModule, QuillModule, RouterModule],
  templateUrl: './bloco-notas.component.html',
  styleUrls: ['./bloco-notas.component.css']
})
export class BlocoNotasComponent {
  anotacoes: Anotacao[] = [];
  userEmail: string = '';
  // Para o editor
  editorAberto = false;
  editorConteudo = '';
  editorTitulo = '';
  quillModules = {
    toolbar: [
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'header': 1 }, { 'header': 2 }],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      [{ 'script': 'sub'}, { 'script': 'super' }],
      [{ 'indent': '-1'}, { 'indent': '+1' }],
      [{ 'direction': 'rtl' }],
      [{ 'size': ['small', false, 'large', 'huge'] }],
      [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'font': [] }],
      [{ 'align': [] }],
      // Sem 'image', sem 'video'
      ['clean']
    ]
  };

  ngOnInit() {
    this.userEmail = localStorage.getItem('userEmail') || '';
    this.carregarAnotacoes();
  }

  carregarAnotacoes() {
    const dados = localStorage.getItem('notas_' + this.userEmail);
    this.anotacoes = dados ? JSON.parse(dados) : [];
  }

  salvarAnotacoes() {
    localStorage.setItem('notas_' + this.userEmail, JSON.stringify(this.anotacoes));
  }

  abrirEditor() {
    this.editorConteudo = '';
    this.editorTitulo = '';
    this.editorAberto = true;
  }

  onEditorChange(event: any) {
    const text = this.stripHtml(event.html || '');
    if (text.length > 300) {
      // Volta para o último valor válido
      this.editorConteudo = event.oldDelta ? event.oldDelta.ops.map((op: any) => op.insert).join('') : this.editorConteudo;
    }
  }

  salvarNovaAnotacao() {
    const plainText = this.stripHtml(this.editorConteudo).slice(0, 300);
    const titulo = this.editorTitulo.slice(0, 50);
    if (plainText.trim() && titulo.trim()) {
      this.anotacoes.push({ titulo, texto: this.editorConteudo, selecionada: false });
      this.salvarAnotacoes();
      this.editorAberto = false;
      this.editorConteudo = '';
      this.editorTitulo = '';
    }
  }

  cancelarEditor() {
    this.editorAberto = false;
    this.editorConteudo = '';
  }

  excluirSelecionadas() {
    this.anotacoes = this.anotacoes.filter(a => !a.selecionada);
    this.salvarAnotacoes();
  }

  stripHtml(html: string): string {
    const div = document.createElement('div');
    div.innerHTML = html;
    return div.textContent || div.innerText || '';
  }
} 