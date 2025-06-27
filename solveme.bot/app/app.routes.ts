// C:\solveme.bot\front-chatbot\src\app\app.routes.ts

import { Routes } from '@angular/router';
// Importe TODOS os componentes que são usados como parte de uma rota
import { HeaderComponent } from './components/header/header.component';
import { FaleConoscoComponent } from './components/fale-conosco/fale-conosco.component';
import { SobreNosComponent } from './components/sobre-nos/sobre-nos.component';
import { LoginComponent } from './components/login/login.component';
import { UsuarioCreateComponent } from './components/usuario/usuario-create/usuario-create.component';
import { UsuarioEditComponent } from './components/usuario/usuario-edit/usuario-edit.component';
import { UsuarioListComponent } from './components/usuario/usuario-list/usuario-list.component';
import { MenuPrincipalComponent } from './components/menu-principal/menu-principal/menu-principal.component';
import { SuporteComponent } from './components/suporte/suporte.component';
import { FaqComponent } from './components/faq/faq.component';
import { BlocoNotasComponent } from './components/bloco-notas/bloco-notas.component';
import { FeedbackComponent } from './components/feedback/feedback.component';
import { PerfilComponent } from './components/perfil/perfil.component';
import { DashbordComponent } from './components/dashbord/dashbord.component';
import { HistoricoComponent } from './components/historico/historico.component';
import { PasswordResetComponent } from './auth/password-reset/password-reset.component';
import { AdminMenuComponent } from './components/admin-menu/admin-menu.component';
import { MuralAtividadesComponent } from './components/mural-atividades/mural-atividades.component';
import { DashbordAdminComponent } from './components/dashbord-admin/dashbord-admin.component';
import { ChatbotComponent } from './components/chatbot/chatbot.component';
import { MuralAtividadesAdminComponent } from './components/mural-atividades-admin/mural-atividades-admin.component';

// Definição das rotas da sua aplicação Angular
export const routes: Routes = [
  {
    path: '', // Rota raiz
    redirectTo: 'login', // Redireciona para a tela de login por padrão
    pathMatch: 'full' // Garante que a URL inteira deve corresponder para o redirecionamento
  },
  { path: 'faleconosco', component: FaleConoscoComponent },
  { path: 'sobrenos', component: SobreNosComponent },
  { path: 'login', component: LoginComponent }, // Rota para a tela de login
  { path: 'usuario/create', component: UsuarioCreateComponent },
  { path: 'usuario/edit/:id', component: UsuarioEditComponent },
  { path: 'usuario', component: UsuarioListComponent },
  { path: 'menu', component: MenuPrincipalComponent }, // Rota para a tela de menu principal
  { path: 'suporte', component: SuporteComponent },
  { path: 'faq', component: FaqComponent },
  { path: 'bloco-notas', component: BlocoNotasComponent },
  { path: 'feedback', component: FeedbackComponent },
  { path: 'perfil', component: PerfilComponent },
  { path: 'dashbord', component: DashbordComponent },
  { path: 'dashbord-admin', component: DashbordAdminComponent },
  { path: 'historico', component: HistoricoComponent },
  { path: 'recuperar-senha', component: PasswordResetComponent },
  { path: 'admin-menu', component: AdminMenuComponent },
  { path: 'mural-atividades', component: MuralAtividadesComponent },
  { path: 'mural-atividades-admin', component: MuralAtividadesAdminComponent },
  { path: 'chat-bot', component: ChatbotComponent }
];