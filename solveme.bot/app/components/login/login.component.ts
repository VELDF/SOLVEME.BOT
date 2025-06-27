// C:\solveme.bot\front-chatbot\src\app\components\login\login.component.ts

import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router'; // Para navegação programática
import { HttpClient } from '@angular/common/http'; // Para fazer requisições HTTP
import { FormsModule } from '@angular/forms'; // Para usar [(ngModel)] no template HTML
import { CommonModule } from '@angular/common'; // Para diretivas como *ngIf no template HTML

import { catchError, throwError } from 'rxjs'; // Operadores RxJS para tratamento de erros
import { finalize } from 'rxjs/operators'; // Operador RxJS para limpeza (ex: desativar loader)

@Component({
  selector: 'app-login',
  standalone: true, // Indica que este é um componente standalone
  imports: [
    FormsModule,      // ESSENCIAL para que [(ngModel)] funcione no seu template HTML
    CommonModule      // ESSENCIAL para diretivas comuns como *ngIf, *ngFor
    // Router e HttpClient são injetados via construtor, não precisam ser importados aqui
  ],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'] // <--- ATENÇÃO: Corrigido para '.css'. Se o seu arquivo for SCSS, mude para './login.component.scss'
})
export class LoginComponent implements OnInit {

  email: string = '';
  password: string = '';
  
  showPassword = false; // Flag para controlar a visibilidade da senha
  isLoading = false;    // Flag para mostrar um loader enquanto a requisição está em andamento
  errorMessage: string = ''; // Mensagem de erro a ser exibida para o usuário

  // Injeção dos serviços Router e HttpClient
  constructor(private router: Router, private http: HttpClient) { }

  ngOnInit(): void {
    // Lógica a ser executada na inicialização do componente (opcional)
  }

  // Alterna a visibilidade do campo de senha
  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  // Método chamado quando o formulário de login é submetido
  login(): void {
    this.isLoading = true; // Ativa o loader
    this.errorMessage = ''; // Limpa mensagens de erro anteriores

    // Payload da requisição POST para o backend
    const loginPayload = {
      email: this.email,
      password: this.password
    };

    // URL do endpoint de login no seu backend (confirme a porta 8001)
    const backendLoginUrl = 'http://localhost:8001/login';

    // Faz a requisição HTTP POST
    this.http.post<any>(backendLoginUrl, loginPayload)
      .pipe(
        // Intercepta e trata erros da requisição
        catchError(error => {
          this.errorMessage = 'Erro ao conectar. Verifique suas credenciais.';
          if (error.status === 401) {
            this.errorMessage = 'Email ou senha inválidos. Tente novamente.';
          } else if (error.error && error.error.detail) {
            this.errorMessage = `Erro: ${error.error.detail}`;
          }
          console.error('Erro de login detalhado:', error);
          return throwError(() => new Error(this.errorMessage)); 
        }),
        // Executa uma ação final, independentemente do sucesso ou falha da requisição
        finalize(() => {
          this.isLoading = false; 
        })
      )
      .subscribe(
        // Lógica para quando a requisição é bem-sucedida
        response => {
          console.log('Login bem-sucedido!', response);
          // Armazena o token JWT e o tipo de token no localStorage do navegador
          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('token_type', response.token_type);

          // Navega para a rota '/menu' após o login bem-sucedido
          this.router.navigate(['/menu']); 
        },
        // Lógica para quando a requisição falha (já tratada principalmente pelo catchError)
        error => {
          console.error('Falha no processo de login:', error);
        }
      );
  }
}