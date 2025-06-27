// C:\solveme.bot\front-chatbot\src\app\app.config.ts

import { ApplicationConfig } from '@angular/core'; // Importa o tipo para a configuração da aplicação
import { provideRouter } from '@angular/router'; // Função para configurar o serviço de roteamento
import { provideHttpClient } from '@angular/common/http'; // Função para configurar o serviço HttpClient

import { routes } from './app.routes'; // Importa a definição das rotas do seu aplicativo

// Define a configuração principal da sua aplicação
export const appConfig: ApplicationConfig = {
  providers: [
    // Fornece o serviço de roteamento para a aplicação, usando as rotas definidas em app.routes.ts
    provideRouter(routes), 
    // Fornece o serviço HttpClient, tornando-o disponível para injeção em qualquer parte da aplicação
    provideHttpClient() 
  ]
};