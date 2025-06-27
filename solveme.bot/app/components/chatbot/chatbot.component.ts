import { Component } from '@angular/core';
import { ChatService } from '../../../app/auth/chat.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-chatbot',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.css']
})
export class ChatbotComponent {
  prompt: string = '';
  loading: boolean = false;
  chatAtivo: boolean = false;

  historico: { pergunta: string; resposta: string }[] = [];

  recentes: string[] = [
    'Como configurar o VPN',
    'Como resetar o MFA',
    'Como executar o mapeamento de pasta'
  ];

  recomendados: string[] = [
    'Instalação do pacote office',
    'Solicitação de instalação',
    'Como configurar a impressora'
  ];

  constructor(private chatService: ChatService) {}

  async sendPrompt() {
    if (!this.prompt.trim()) return;

    const pergunta = this.prompt;
    this.prompt = '';
    this.loading = true;
    this.chatAtivo = true;

    let resposta = '';
    for await (const chunk of this.chatService.sendPromptStreaming(pergunta)) {
      resposta += chunk;
    }

    this.historico.push({ pergunta, resposta });
    this.loading = false;
  }

  sendSuggestion(text: string) {
    this.prompt = text;
    this.sendPrompt();
  }

  resetChat() {
    this.prompt = '';
    this.loading = false;
    this.chatAtivo = false;
    this.historico = [];
  }

  copiarTexto(texto: string) {
    navigator.clipboard.writeText(texto).then(() => {
      console.log('Texto copiado!');
    });
  }

  rolarParaTopo() {
    const el = document.querySelector('.chat-container');
    if (el) el.scrollTo({ top: 0, behavior: 'smooth' });
  }
}
