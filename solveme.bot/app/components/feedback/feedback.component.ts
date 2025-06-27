import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-feedback',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './feedback.component.html',
  styleUrls: ['./feedback.component.css']
})
export class FeedbackComponent {
  opcoes = [
    { icon: '🐞', label: 'Problema', placeholder: 'Algo não está funcionando bem? Queremos corrigir. Conte com detalhes o que está acontecendo...' },
    { icon: '💡', label: 'Ideia', placeholder: 'Tem uma sugestão ou ideia para melhorar? Compartilhe com a gente!' },
    { icon: '💬', label: 'Outro', placeholder: 'Outro tipo de feedback? Escreva aqui.' }
  ];

  etapa: 'escolha' | 'detalhe' = 'escolha';
  opcaoSelecionada: any = null;
  mensagem: string = '';

  selecionarOpcao(opcao: any) {
    this.opcaoSelecionada = opcao;
    this.etapa = 'detalhe';
    this.mensagem = '';
  }

  voltar() {
    if (this.etapa === 'detalhe') {
      this.etapa = 'escolha';
      this.opcaoSelecionada = null;
      this.mensagem = '';
    } else {
      // Volta para o menu
      window.history.back();
    }
  }

  enviarFeedback() {
    // Aqui você pode implementar o envio real do feedback
    alert('Feedback enviado! Obrigado.');
    this.etapa = 'escolha';
    this.opcaoSelecionada = null;
    this.mensagem = '';
  }
} 