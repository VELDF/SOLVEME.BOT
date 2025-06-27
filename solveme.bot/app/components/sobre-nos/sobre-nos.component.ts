import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-sobre-nos',
  imports: [CommonModule],
  templateUrl: './sobre-nos.component.html',
  styleUrl: './sobre-nos.component.css'
})
export class SobreNosComponent {
  faqs = [
    {
      pergunta: 'O que é o SolveMe Bot?',
      resposta: 'É um assistente virtual para automatizar tarefas dentro das empresas.',
      aberto: false
    },
    {
      pergunta: 'Quem pode usar o SolveMe Bot?',
      resposta: 'Qualquer empresa que queira otimizar o atendimento e processos internos.',
      aberto: false
    },
    {
      pergunta: 'O SolveMe Bot precisa de internet?',
      resposta: 'Sim, ele funciona via web e precisa de conexão com a internet.',
      aberto: false
    },
    {
      pergunta: 'É necessário treinamento para usar o SolveMe Bot?',
      resposta: 'Não, a interface é intuitiva e fácil de usar, com suporte disponível se necessário.',
      aberto: false
    },
    {
      pergunta: 'Quais são os principais recursos do SolveMe Bot?',
      resposta: 'Automação de atendimento, organização de processos, respostas rápidas e integração com sistemas.',
      aberto: false
    }
  ];

  toggleFaq(index: number) {
    this.faqs[index].aberto = !this.faqs[index].aberto;
  }
}