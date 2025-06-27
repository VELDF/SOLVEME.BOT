import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-dashbord',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashbord.component.html',
  styleUrls: ['./dashbord.component.css']
})
export class DashbordComponent {
  categorias = [
    { nome: 'Impressoras', valor: 9 },
    { nome: 'Redes', valor: 12 },
    { nome: 'Software', valor: 17 },
    { nome: 'Outros', valor: 22 }
  ];

get maxValor(): number {
  return Math.max(...this.categorias.map(c => c.valor), 1); // evita divisão por zero
}

calcularAltura(valor: number): string {
  return `${(valor / this.maxValor) * 100}%`;
}

voltar() {
  window.history.back();
}

}
