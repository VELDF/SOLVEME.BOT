// C:\solveme.bot\front-chatbot\src\app\app.component.ts

import { Component } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router'; // RouterOutlet é necessário para exibir as rotas
import { HeaderComponent } from './components/header/header.component';
import { FooterComponent } from './components/footer/footer.component';
import { NgIf } from '@angular/common'; // Necessário para diretivas como *ngIf
import { FormsModule } from '@angular/forms'; // Necessário se houver [(ngModel)] ou formulários em templates filhos não standalone
import { ReactiveFormsModule } from '@angular/forms'; // Necessário se houver formulários reativos em templates filhos não standalone
// Importe SOMENTE os componentes que são usados DIRETAMENTE no template de app.component.html
// Componentes carregados via roteador (como LoginComponent, MenuPrincipalComponent, etc.) NÃO devem ser importados aqui.

@Component({
  selector: 'app-root',
  standalone: true, // Indica que este é um componente standalone
  imports: [
    RouterOutlet,          // Permite que as rotas sejam carregadas e exibidas
    HeaderComponent,       // Importa o componente do cabeçalho
    FooterComponent,       // Importa o componente do rodapé
    NgIf,                  // Importa o módulo para a diretiva *ngIf
    FormsModule,           // Importa o módulo para formulários baseados em template
    ReactiveFormsModule    // Importa o módulo para formulários reativos
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css' // ATENÇÃO: Verifique se o seu arquivo de estilo é .css ou .scss
})
export class AppComponent {
  title = 'front-ChatBot';

  // O Router é injetado para permitir acessar a URL atual e outras funcionalidades de roteamento
  constructor(public router: Router) {}

  // Método para verificar se a página atual é a de login ou recuperação de senha
  isLoginPage(): boolean {
    return ['/login', '/recuperar-senha'].includes(this.router.url);
  }
}