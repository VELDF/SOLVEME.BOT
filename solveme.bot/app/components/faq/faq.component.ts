import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface FaqItem {
  question: string;
  answer: string;
}

@Component({
  selector: 'app-faq',
  standalone: true,
  imports: [RouterModule, CommonModule, FormsModule],
  templateUrl: './faq.component.html',
  styleUrls: ['./faq.component.css']
})
export class FaqComponent {
  openIndex: number | null = 0;
  searchTerm: string = '';

  faqs: FaqItem[] = [
    {
      question: 'O que é o SolveMe Bot?',
      answer: 'É um assistente virtual para automatizar tarefas dentro das empresas.',
    },
    {
      question: 'Como posso alterar minha senha?',
      answer: 'Para alterar a senha, vá para a página de "Perfil" do sistema, selecione o botão "Alterar Senha" e siga as instruções seguintes.'
    },
    {
      question: 'Como posso contatar o suporte?',
      answer: 'Você pode contatar o suporte pela aba "Suporte" do menu ou pelo e-mail suporte@solveme.com.'
    },
    {
      question: 'Quem pode usar o SolveMe Bot?',
      answer: 'Qualquer empresa que queira otimizar o atendimento e processos internos.',
    },
    {
      question: 'O SolveMe Bot precisa de internet?',
      answer: 'Sim, ele funciona via web e precisa de conexão com a internet.',
    },
    {
      question: 'É necessário treinamento para usar o SolveMe Bot?',
      answer: 'Não, a interface é intuitiva e fácil de usar, com suporte disponível se necessário.',

    },
    {
      question: 'Quais são os principais recursos do SolveMe Bot?',
      answer: 'Automação de atendimento, organização de processos, respostas rápidas e integração com sistemas.',
    }
  ];

  get filteredFaqs(): FaqItem[] {
    if (!this.searchTerm.trim()) return this.faqs;
    return this.faqs.filter(faq =>
      faq.question.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
      faq.answer.toLowerCase().includes(this.searchTerm.toLowerCase())
    );
  }

  toggle(index: number) {
    this.openIndex = this.openIndex === index ? null : index;
  }
} 