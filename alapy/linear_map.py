import sympy as sp

from alapy.math_set import *
from alapy.vector_space import VectorSpace
from alapy.utils import of_arity, is_invertible

class LinearMapError(Exception):
    def __init__(self, msg=''):
        super().__init__(msg)

class IsomorphismError(Exception):
    def __init__(self, msg=''):
        super().__init__(msg)

class LinearMap:
    def __init__(self, domain, codomain, mapping=None, matrix=None, name=None):
        if not isinstance(domain, VectorSpace):
            raise TypeError('The domain must be a VectorSpace.')
        if not isinstance(codomain, VectorSpace):
            raise TypeError('The codomain must be a VectorSpace.')
        if mapping is None and matrix is None:
            raise LinearMapError('Either a matrix or mapping must be provided.')
        if domain.field is not codomain.field:
            raise LinearMapError('The domain and codomain must be vector spaces '
                                 'over the same field.')
        
        if mapping is None:
            mapping = LinearMap._from_matrix(domain, codomain, matrix)
        elif not of_arity(mapping, 1):
            raise TypeError('Mapping must be a function of arity 1.')
        if matrix is None:
            matrix = LinearMap._to_matrix(domain, codomain, mapping)
        else:
            matrix = sp.Matrix(matrix)
        
        self._domain = domain
        self._codomain = codomain
        self._mapping = mapping
        self._matrix = matrix
        if name is not None:
            self.__name__ = name

    @staticmethod
    def _to_matrix(domain, codomain, mapping):
        matrix = []
        for vec in domain.basis:
            mapped_vec = mapping(vec)
            coord_vec = codomain.to_coordinate(mapped_vec)
            matrix.append(coord_vec)
        return sp.Matrix(matrix).T

    @staticmethod
    def _from_matrix(domain, codomain, matrix):
        matrix = sp.Matrix(matrix)
        to_coord = domain.to_coordinate
        from_coord = codomain.from_coordinate
        return lambda vec: from_coord(matrix @ to_coord(vec))

    @property
    def domain(self):
        return self._domain
    
    @property
    def codomain(self):
        return self._codomain
    
    @property
    def mapping(self):
        return self._mapping
    
    @property
    def matrix(self):
        return self._matrix
    
    @property
    def field(self):
        return self.domain.field
    
    def __repr__(self):
        return (f'LinearMap(domain={self.domain}, codomain={self.codomain}, '
                f'mapping={self.mapping.__name__})')
    
    def __str__(self):
        if hasattr(self, '__name__'):
            return f'{self.__name__}: {self.domain} -> {self.codomain}'
        else:
            return self.__repr__()

    def __eq__(self, map2):
        return (self.domain == map2.domain and self.codomain == map2.codomain and 
                self.matrix == map2.matrix)
    
    def __add__(self, map2):
        mapping = lambda vec: self.mapping(vec) + map2.mapping(vec)
        matrix = self.matrix + map2.matrix
        return LinearMap(self.domain, self.codomain, mapping, matrix)
    
    def __mul__(self, scalar):
        if not isinstance(scalar, self.field):
            raise TypeError('Scalar must be an element of the vector space field.')
        mapping = lambda vec: self.mapping(vec) * scalar
        matrix = self.matrix * scalar
        return LinearMap(self.domain, self.codomain, mapping, matrix)
    
    def __rmul__(self, scalar):
        if not isinstance(scalar, self.field):
            raise TypeError('Scalar must be an element of the vector space field.')
        mapping = lambda vec: scalar * self.mapping(vec)
        matrix = scalar * self.matrix
        return LinearMap(self.domain, self.codomain, mapping, matrix)
    
    def __call__(self, vec):
        if vec not in self.domain:
            raise TypeError(f'{vec} is not an element of the domain.')
        return self.mapping(vec)
    
    def composition(self, map2):
        if self.domain != map2.codomain:
            raise LinearMapError('The linear maps are not compatible.')
        
        mapping = lambda vec: self.mapping(map2.mapping(vec))
        matrix = self.matrix @ map2.matrix  # check
        if hasattr(self, '__name__') and hasattr(map2, '__name__'):
            name = f'{self.__name__} o {map2.__name__}'
        else:
            name = None
        return LinearMap(map2.domain, self.codomain, mapping, matrix, name)
    
    def nullspace(self):
        pass
    
    def range(self):
        pass

# is_injective, is_surjective
class Isomorphism(LinearMap):
    def __init__(self, domain, codomain, mapping=None, matrix=None, name=None):
        super().__init__(domain, codomain, mapping, matrix, name)

        if not is_invertible(self.matrix):
            raise IsomorphismError('Linear map is not invertible.')

    def __repr__(self):
        return (f'Isomorphism(domain={self.domain}, codomain={self.codomain}, '
                f'mapping={self.mapping.__name__})')
    
    def inverse(self):
        matrix = self.matrix.inv()
        return Isomorphism(self.codomain, self.domain, matrix=matrix)


class IdentityMap(Isomorphism):
    def __init__(self, vectorspace, name=None):
        super().__init__(vectorspace, vectorspace, lambda vec: vec, name=name)