import { Component } from '@angular/core';
import { CommonModule } from '@angular/common'; 

@Component({
  selector: 'app-mural-atividades-admin',
  imports: [CommonModule],
  templateUrl: './mural-atividades-admin.component.html',
  styleUrl: './mural-atividades-admin.component.css'
})
export class MuralAtividadesAdminComponent {


  funcionarios = [
    { nome: 'Alex Mason', alerta: true },
    { nome: 'Ana Sofia', alerta: true },
    { nome: 'Marcelo Miguel', alerta: true },
    { nome: 'Karen Raquel', alerta: true },
    { nome: 'Gabriel Vicenzo', alerta: true }
  ];


  voltar() {
      window.history.back();
      }
}
