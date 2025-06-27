import { Component } from '@angular/core';
import { FormGroup, FormControl, Validators, ReactiveFormsModule } from '@angular/forms';
import { AuthService } from '../../../auth/auth.service'; // ajuste o caminho

@Component({
  selector: 'app-usuario-create',
  standalone: true,                 // <- aqui!
  imports: [ReactiveFormsModule],   // <- importa o módulo aqui
  templateUrl: './usuario-create.component.html',
  styleUrls: ['./usuario-create.component.css']  // corrigido plural
})
export class UsuarioCreateComponent {
  userForm = new FormGroup({
    name: new FormControl('', Validators.required),
    email: new FormControl('', [Validators.required, Validators.email]),
    telefone: new FormControl(''),
    password: new FormControl('', Validators.required),
    setor: new FormControl('')
  });


    constructor(private authService: AuthService) {}

  onSubmit() {
    if (this.userForm.valid) {
      const { name, email, password } = this.userForm.value;
      // Seu backend atualmente espera name, email e password
      this.authService.register(name!, email!, password!).subscribe({
        next: () => alert('Usuário cadastrado com sucesso!'),
        error: () => alert('Erro no cadastro, tente novamente.')
      });
    } else {
      alert('Preencha corretamente os campos obrigatórios.');
    }
  }
}
