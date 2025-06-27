import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { routes } from '../../../app.routes';

@Component({
  selector: 'app-menu-principal',
  standalone: true,
  imports: [CommonModule, RouterModule], 
  templateUrl: './menu-principal.component.html',
  styleUrls: ['./menu-principal.component.css']
})
export class MenuPrincipalComponent {

  
  menuItems = [
    {
      icon: '📊',
      title: 'Dashboard',
      description: 'Visualize seu desempenho e atividades recentes',
       route: '/dashbord'
    },
    {
      icon: '📖',
      title: 'Mural de Atividades',
      description: 'Acompanhe atualizações e interações da equipe',
      route: '/mural-atividades'
    },
    {
      icon: '👤',
      title: 'Perfil',
      description: 'Atualize seus dados pessoais e senha',
      route: '/perfil'
    },
    {
      icon: '📝',
      title: 'Bloco de Notas',
      description: 'Crie e organize suas anotações pessoais',
      route: '/bloco-notas'
    },
    {
      icon: '⭐',
      title: 'Feedback',
      description: 'Dê sua opinião sobre o atendimento recebido',
      route: '/feedback'
    },
    {
      icon: '❓',
      title: 'FAQ / Central de Ajuda',
      description: 'Encontre respostas rápidas para dúvidas comuns',
      route: '/faq'
    },
    {
      icon: '💬',
      title: 'Histórico de Conversas',
      description: 'Consulte conversas anteriores com o bot',
      route: '/historico'
    },
    {
      icon: '🏢',
      title: 'Central do administrador',
      description: '(admin) registro de funcionários, caixas e cadastro de funcionários',
      route: '/admin-menu'
    },
    {
      icon: '🤖',
      title: 'Chat Bot',
      description: 'Fale com o Solveme Bot para tirar suas dúvidas',
      route: '/chat-bot'
    }
  ];

}